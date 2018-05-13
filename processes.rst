.. _processes:

Development processes in Docker
===============================

Whilst developing it is not unusually to have one off processes that need to be run on an ad-hoc basis. The most
obvious example would be the test suite runner but it also extends to code linters and static analysis tools. Within
the Django_ development process there are also the management tasks to create and run migrations, or to open a Python
shell in a Django context.

Before Docker_ this would mean running them directly on your machine in a local terminal window. Now, with your
development environment residing within a Docker_ container it is not so obvious how you can run these things when
needed.

There are 2 different approaches that could be taken here. One is that one off management task should be run in one off
ephemeral containers. This approach would work fine for things like running the test suite. We would spin up a new
container, mount our code in the container, run the test suite and tear it all back down again.

Where this approach does not work so well, specifically in the Python_ world, is around keeping your virtual
environment up to date. If you add a new requirement to your project you need a mechanism to update the virtual
environment inside the container. The most obvious approach would be to simply re-build the container during which the
new requirement would be picked up and installed. This should perhaps be your approach from time to time to ensure that
you have fully defined all your projects requirements. However, the process of rebuilding the container can be a little
slow, even with Docker_ caching intermediate layers.

What you really want is to be able to install that new dependency in the existing virtual environment within you
already running container. This is particularly true when what you want to install is something like a debugging tool
you need just to help resolve a specific issue, or when trialling new packages.

Best practice with Docker_ is that your containers should run one thing or at least only 1 *type* of thing. For example
our Django_ development environment runs the Django_ development server. Given these one off tasks are ephemeral, that
we want them to effect the already running container and that this is after all a development environment I think we
can be forgiven if we run additional processes in our running container.


Docker Exec
-----------

To execute a command within a running container the Docker_ command line tool provides the ``exec`` command which is
used as follows:


.. code-block:: bash

    docker exec my_container /some/application/binary


That is it takes the name (or id) or your running docker container, and the command you wish it to run. This does
pretty much what you would expect it to, run your command.

You can also use most of the same command line switches as the ``docker run`` command, like environmental variables and
perhaps most importantly ``-it`` for and interactive terminal. i.e. the ability to work with whatever program you just
started. There isn't much point running say ``./manage.py shell`` if you can't type into the shell it presents you
with.

So to take the example activity we used above of updating our virtual environment with new dependencies we can do the
following:


.. code-block:: bash

    docker exec -it my_container /venv/bin/pip install -r /path/to/requirements.txt


You'll note that in the above command I used the full path to the version of ``pip`` installed within the containers
virtual environment. This is important. If I didn't use the full path the container would look through the directories
defined in it's path and possible select the wrong version of ``pip`` and install the requirements outside the virtual
environment. Or fail to locate ``pip`` entirely and not install anything. It could alternatively be written as
something like:

.. code-block:: bash

    docker exec -it my_container "source /venv/bin/activate && pip install -r /path/to/requirements.txt"


This can get a little cumbersome to work with, not only do you have to remember (or work out) the name of the container
you currently have running but also all the command line switches like ``-it``. So to make things a little easy I have
put together a little tool called Rind_ that takes care of a lot of this for you.

Rind
----

Rind_ (Run in Docker) is a simple command line tool for executing things inside docker containers

Effectively anything passed as a command line argument is executed directly within the rind enabled container. e.g.

.. code-block:: bash

    rind ./manage.py migration


Would run the ``manage.py`` script in the containers working directory, passing it the ``migrate`` argument

If no parameters are passed to ``rind`` then the default ``/bin/sh`` is used which will give you and interactive
terminal.

Rind_ itself is written in Python_ but the prefered installation method would be to download the appropiate binary from
the releases_ page and install it somewhere on your ``PATH``.

So how does Rind_ know which container to run your command in, you could be running multiple containers for any given
project after all?  The answer lies in a feature of Docker_, the ability to assign **labels** to your containers.

To rind_ enable a container you need to add a  ``app.rind`` label to it. You can do this in your
``docker-compose.yml`` file:

.. code-block:: yaml

    services:
        a_service:
            image: an_image
            labels:
                - app.rind


.. warning::

    At present `Rind`_ supports only a single running container with the ``app.rind`` label. If more than one are found
    then it cannot determine which the command should run within. This may change in the future but it is currently a
    limitation.


Rind_ also has the ability to run pre-steps when executing inside the container. For example activating a Python
virtual environment.

To enable a pre-step you need to add it as a value to your label. For example, activating a Python_ ``virtualenv`` can
be achieved as follows:

.. code-block:: yaml

    services:
        a_service:
            image: an_image
            labels:
                app.rind: "source /venv/bin/activate"


This assumes you virtual environment is situated at ``/venv`` within the Docker_ container.


.. _django: https://www.djangoproject.com
.. _docker: https://www.docker.com
.. _python: https://www.python.org
.. _rind: https://github.com/a-musing-moose/rind
.. _releases: https://github.com/a-musing-moose/rind/releases
