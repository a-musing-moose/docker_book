.. _project:

A Project Starter
=================


The directory structure below details the layout of a typical Django_ project you might work on, adapted for use with a
Dockerised workflow. In this chapter we will explore this and take a look into the various parts of it.

::

    ├── app
    │   ├── base
    │   │   ├── __init__.py
    │   │   ├── settings.py
    │   │   ├── urls.py
    │   │   └── wsgi.py
    │   ├── bootstrap.sh
    │   ├── manage.py
    │   ├── requirements
    │   │   ├── base.txt
    │   │   └── local.txt
    │   ├── setup.cfg
    │   ├── static
    │   ├── tests
    │   │   ├── behavioural
    │   │   ├── integration
    │   │   └── unit
    │   └── uwsgi.ini
    ├── deployment
    │   ├── config
    │   │   └── allowed_hosts
    │   ├── secrets
    │   │   └── database_url
    │   └── stack.yml
    ├── docker-compose.override.yml
    ├── docker-compose.yml
    ├── Dockerfile
    ├── Dockerfile.local
    ├── docs
    ├── Makefile
    └── README.rst


This example project is also available on GitHub_ at
https://github.com/a-musing-moose/docker_book/tree/master/examples/django

.. todo::
    Should I separate these from the book repo?


Project Components
------------------

app/
    This is the actual Django application along with it's tests

deployment/
    Configuration and tools involved in deployment of the applications.

docker-compose{.override}.yml
    Configuration for local development setup

Dockerfile{.local}
    Build rules for the Docker_ images

docs/
    In here you can find the documentation for the project

Makefile
    Helpful little functions for developers like kicking of tests, building Docker_ images, running formatting tools
    etc.

README.rst
    The readme of any project should provide, at minimum, a brief description of what the project actually is and how
    to get it up and running.


Dockerfiles
-----------

Dockerfiles are the recipes by which Docker_ builds images. They are simple set of instructions defining the steps that
the Docker_ engine needs to follow. The simplest of all containers I could think of is one that does nothing more than
echo "Hello, world" when run.  The Dockerfile to achieve that would look like this:

.. code-block:: Dockerfile

    FROM alpine:3.7
    CMD echo "Hello, World"

In our example project we have 2 separate Dockerfiles currently, ``Dockerfile`` and ``Dockerfile.local``. They have 2
different roles. The ``Dockerfile.local`` one is used exclusively for development. It take a simple approach to
building the image and by default when run will run the Django_ development server.

``Dockerfile`` is actually the default filename that Docker_ will look for when you tell it to build an image, in this
project it is the set of instructions that we want to use when build the application for production deployment. The
command it runs by default is a production grade :abbr:`WSGI (Web Server Gateway Interface)` capable server. In this
case uWSGI_

These 2 files take different approaches to do very similar things, and explaining a little how Docker_ does filesystems
will help explain why.

The ``Docker.local`` looks something like this:

.. code-block:: Dockerfile

    FROM python:3.6.4-alpine

    # Create the directory layout and virtual environment
    RUN mkdir /venv /app && python3.6 -m venv /venv

    RUN apk add --no-cache postgresql-libs build-base linux-headers postgresql-dev git
    COPY app/requirements /app/requirements
    RUN /venv/bin/pip install -r /app/requirements/local.txt
    WORKDIR /app
    CMD /venv/bin/python manage.py runserver 0.0.0.0:8000


You can see that each line (except for the commented ones) is own it's own line, and that each line starts with an
uppercase keyword. e.g. ``RUN``. When Docker_ is building an image it does so in layers. Each line in the Dockerfile
that starts with one of the keywords represents a new layer. Once the new layer is created it becomes read-only,
immutable. In fact Docker_ will give each layer a unique hash value. It is the combination of it's immutablility
combined with it's unique identifier that makes it ideal for development. During the build process Docker_ will check
to see if anything with a specific layer has changed since it was last built. If there are have been now changes then
it will re-use the existing layer. Making the build potentially a lot faster.

As an exmaple, if we made a change in the requirements associated with this project and asked Docker_ to rebuild our
image, it would be able to re-use the first 3 layers defined (the FROM, RUN and RUN). Only when it got to the
``COPY app/requirements /app/requirements`` step would it need to start doing anything. Once Docker_ reaches a step
that requires work, that step and every one after is marked for re-building.

So you cna now see how Docker's layer caching can help keep things moving during development, but it extends to
pushing your images to a registry as well as pulling from a registry during deployment.

When you ask to push or pull an image it goes through a similar process, the local and remote sides will negotiate
over what layers need to be transfered and will avoid re-transfering layers they already have. This applies not just
for different versions of the same image, but also across images. If for example I have already pulled the
``python:3-6.4-alpine`` image, or even another one based on it I would already have the layers from that image and
would not need to pull them again.

Moving onto the second file, ``Dockerfile`` it does things slightly differently and highlights an often overlooked
drawback to immutable layers.


.. code-block:: Dockerfile

    FROM python:3.6.4-alpine

    # Create the directory layout and virtual environment
    RUN mkdir /venv /app /static && python3.6 -m venv /venv

    COPY app/requirements /app/requirements

    RUN apk add --no-cache postgresql-libs \
        && apk add --no-cache --virtual build-deps build-base linux-headers postgresql-dev \
        && /venv/bin/pip install -r /app/requirements/base.txt \
        && apk del build-deps

    COPY app /app/

    RUN /venv/bin/python /app/manage.py collectstatic --noinput
    EXPOSE 80

    CMD /app/bootstrap.sh


For the first 3 steps, things look the same. It is only when we come to the 4th step things start to change. This step
starts in a similar way with an ``apk add``, which is the way you install system packages on `Alpine Linux`_. But
rather than doing a separate ``RUN`` for each subsiquent command they have been bundled up into a single run statement
using ``&&`` to chain them together and ``\`` to allow us to split them over multiple lines. The effect of this might
not be entirely obvious but it ensures that all the work done inside those various lines is considered as a single
layer in the image that is created. There is of course a side effect that if any changes to the list of system packages
*or* Python packages is made it will have to re-run this rather large step which is very time consuming. So why would
we want to do this?

The answer lies in what this step is doing:

1. Install runtime system dependencies (the PostgreSQL_ client library)
2. Install buildtime system dependencies (Linux header, build tools etc.)
3. Installing (and building where necessary) Python specific runtime dependencies
4. Uninstalling the buildtime system dependencies installed in part 2.

It is that final part, the uninstall that necessitates the combining of these 4 parts into a single step. From what we
know about how Docker_ manages layers, if these were each independent steps then a layer including the build time
dependencies would be created, and whislt they would never be usable or accessible from the final image, the layer
would never the less be part of the overall image, increasing it's total size. By doing the install, build, uninstall
in a single step we avoid the devleopment tools, the build time only dependencies ever getting commited to a layer.
Keeping our final, distributable images small and nible.

From the 2 approaches you can see that the image build process can be optimized in different ways, for reusability
during development or for size when targetting deployment. Whether you feel the trade-offs and overheads of maintaining
2 separate Dockerfiles is worth while will depend on your own situation.


Volumes
-------

.. todo::

    Talk about mapping local code folder to one inside the container.


Running it using just Docker
----------------------------

Running this stack with just Docker_ itself is somewhat labourious and is included here just reference, save yourself
the hassle and never do this yourself!

.. code-block:: base

    # Start the database server
    docker run --name=base_db -d -e POSTGRES_DB=dev_db -e POSTGRES_USER=dev_user POSTGRES_PASSWORD=dev_password -p "5432:5432" postgres:10

    # Start the documentation server again in the background
    docker run --name=base_docs -p "8080:8000" -v "<full/local/path>:/docs" moose/sphinx

    # Then build are development image
    docker build -t base/web .

    # Finally run the dev container
    docker run --name=base_web -e DEBUG=True -p  "8000:8000" -p "6889:6889" --link=base_db --label "app.rind=source /venv/bin/activate" -v "<full/local/path>:/app" base/web


Quite a mouthful to remember and even more to explain to someone just picking up the project. Since the first 2 are
set to run in the background with the ``-d`` (*detached*) flag you will not be able to see their output directly. You
will need to use ``docker log`` instead.


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
.. _django: https://www.djangoproject.com/
.. _uwsgi: https://uwsgi-docs.readthedocs.io/en/latest/
.. _`alpine linux`: https://alpinelinux.org/
.. _PostgreSQL: https://www.postgresql.org/
