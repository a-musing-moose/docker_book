.. _project:

A Project Starter
=================


An example Django project

.. todo::
     - Deployment stackfile
     - This is Django specific, could it be just *Python* specific?

::

    project/
    ├── Dockerfile
    ├── Dockerfile.local
    ├── Makefile
    ├── README.rst
    ├── app
    │   ├── bootstrap.sh
    │   ├── features
    │   │   ├── example.feature
    │   │   └── steps
    │   │       └── example.py
    │   ├── manage.py
    │   ├── requirements
    │   │   ├── base.txt
    │   │   └── local.txt
    │   ├── setup.cfg
    │   ├── static
    │   ├── tests
    │   │   ├── __init__.py
    │   │   └── example_tests.py
    │   ├── project_name
    │   │   ├── __init__.py
    │   │   ├── settings.py
    │   │   ├── urls.py
    │   │   └── wsgi.py
    │   └── uwsgi.ini
    ├── docker-compose.yml
    └── docs


The directory structure above details the layout of a typical Django project you might work on, adapted for use with a
Dockerised workflow. In this chapter we will explore this and take a deep dive into the various parts of it.

This example project is also available on GitHub_ at XXX

.. todo::
    Push example project to github and make public


Dockerfiles
-----------

Dockerfiles are the recipes by which Docker_ builds images. They are simple set of instructions defining the steps that
the Docker_ engine needs to follow. The simplest of all containers I could think of is one that does nothing more than
echo "Hello, world" when run.  The Dockerfile to achieve that would look like this:

.. code-block:: Dockerfile

    FROM alpine:3.7
    CMD echo "Hello, World"


Volumes
-------

.. todo::

    Talk about mapping local code folder to one inside the container.


Running it using just Docker
----------------------------

.. todo::

    Labourious steps to run multiple containers locally to highlight how awesome docker-compose is. Waiting on a
    functional project to ensure all containers covered


Docker Compose
--------------

Remember in the :ref:`containers` section were I recommended that you install docker-compose_, that whole last section
is why. Having to remember all the command line options and switch can be painful and it is easy to forget something by
accident. Docker-compose_ takes a lot of the repetition out of the process. You can do all the configuration once,
record it in one place and share it with all the other team members.

Docker-compose_ is a tool for defining multi-container applications and then running them without the need for long and
complicated command lines. To do this you define your application in a :abbr:`YAML (Yet Another Markup Language)` file,
this file allows you to specify what container need to be run, what ports should be exposed, and a whole bunch of other
configuration options. Pretty much anything you can specify via the command line can also be defined in the
``docker-compose.yml`` file.

.. note::
    The format of the ``docker-compose.yml`` file is very similar and in some cases identical to the deployment config
    files used by a number of container orchestration systems.

Once that is done, you can start all the containers using (assuming the ``docker-compose.yml`` file is in the current
directory):

.. code-block:: bash

    $ docker-compose up


This will start all the containers specified in your ``docker-compose.yml`` file and print anything they output to your
terminal.

You can stop them by using ``ctrl+c`` or in another shell:

.. code-block:: bash

    $ docker-compose stop


.. warning::

    There is also ``docker-compose down`` which seems the most obvious counter command to ``up``. However, ``down`` not
    only stop the containers, but will destroy them too. Which I guess is the counter to ``up`` but probably not what
    you actually want to happen.


.. todo::

    Explain the use of ``docker-compose.override.yml``

.. _github: https://github.com
.. _docker-compose: https://docs.docker.com/compose/
.. _docker: https://docker.com/
