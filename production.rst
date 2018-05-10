.. _production:

Taking it to Productions
========================


Docker Registries
-----------------

Up until now we have be working with building images locally, or at most pulling pre-built images. So how does Docker_
find images when you ask for one that isn't already available locally? It tries to pull it from the
`official Docker registry`_.

When we start moving to production, we need some way to make our locally build, grass-fed Docker_ images available to
our production environment. The mechanism of choice is once again a Docker_ registry. We have a couple of options here,
we can either create a paid account on the `official Docker registry`_ or we can host our own private registry.

If we choose the  `official Docker registry`_ then the only change we need to make it to ensure that when deploying
we provide the Docker_ engine running on our production environment access credentials to authenticate itself and gain
access to our private images.

Docker_ are also nice enough to provide an implementation of the `Docker registry`_ packaged up as a Docker_ image for
us to run. This take a little configuration, especially if we want to ensure that it is fully secured with SSL
certificates. But a paid for account on the `official Docker registry`_ is not an option then this is a good
alternative.


Simple, Single Container Deployments
------------------------------------

.. todo::

    Docker compose and/or Dokku. Could also be simply ``docker run`` with a restart policy


Docker: Swarm Mode
------------------

`Swarm mode`_ is the light weight cluster management solution built into Docker_. It allows you to treat a collection
of devices like one, large device. The swarm itself takes care of things like what container runs where, and networking
between nodes in the cluster. It also allows you to easily scale invidual container types (known as services when
running in swarm mode).

So for example I might have a image of an HTTP server that need to listen on Port ``80``. I can inform the swarm to run
4 instances of this service. It will then take care of distributing those instance across nodes in the swarm. In
addition, every node in the cluster will start listening on port ``80``. You can make a request to any node in the
cluster on port ``80`` and it will route the request automatically to a node on which one of the HTTP server instances
is being run.


Installation
^^^^^^^^^^^^

If you have Docker_ installed then you already have everything you need to start a swarm.

.. code-block:: bash

    $ docker swarm init
    Swarm initialized: current node (p1hhmb3xlkkgcdthu2kg2lceh) is now a manager.

    To add a worker to this swarm, run the following command:

        docker swarm join --token <some-realy-long-string> 192.168.1.169:2377

    To add a manager to this swarm, run 'docker swarm join-token manager' and follow the instructions.


It may complain, as it did on my machine, that is needs to be told the advertised address, i.e. the IP address to which
it should bind to allow other nodes in the swarm to talk to it. If the ``init`` command asks you can specify one with
the ``--advertise-addr`` command line switch.

You may also have notices in the console output that it talked about **workers** and **managers**. Manager nodes are
responsible to dispatching tasks (e.g. "run this container") to a worker. It is to a manager node that you would submit
your service definitions.

There is only 1 leader of a cluster, but it is automatically elected from available manager nodes. The leader is
responsible for maintaining the desired state of the cluster.

Workers on the other hand have no role in maintaining the cluster itself, their sole responsibilty is to run the tasks
assigned by a  manager and keep the manager up to date on the status of those tasks.

By default, tasks can also be assigned to manager nodes. The manager node acts as both a manager and a worker. this
behaviour can be disabled if desired.

From the command line output of the swarm mode initialisation you can also see instructions on have to add new worker
and manager nodes to the cluster.

.. note::

    You can add and remove nodes from a swarm at any time. The cluster will re-distribute the workload to ensure that
    the cluster is in the desired state. Note however, that a swarm must have at least 1 manager node to exist. More to
    provide resilience.


Services and Stacks
^^^^^^^^^^^^^^^^^^^

You may have noticed in the last section that I started talking about **services**, and stopped talking about
**containers**. When running Docker_ images in swarm mode, a single image may be run multiple times across the cluster.
For this reason we refer to them as services rather than just containers. A service is really just the definition of
the tasks that the cluster needs to execute. There are 2 broad categories of services, **replicated services** and
**global services**.

Replicated services are those that the swarm will distribute a specific number of instances across that cluster. You
can scale this number up and down.

Global services are those which the swarm will ensure run on every node in a cluster. Useful so node monitoring for
example.

A new service can be created in a similar manner as a new containers are started.

.. code-block:: bash

    $ docker service create <options> IMAGE <command> <args...>


This will create a new service with the specified image, and scale it to 1 instance.

You can also easily see what services are running with:

.. code-block:: bash

    $ docker service ls


Scaling your service instances up or down is equally as easy:

.. code-block:: bash

    $ docker service scale <service_name>=<number of replicas> [<service_name>=<number of replicas>...]


As with running Docker_ containers locally, defining services by hand each time can be repeatitive and error prone. As
you have seen, when working locally you can created a ``docker-compose.yml`` to allow you to spin up and configure
multiple containers locally. That same file can be use to deploy and configure a series of services. Again, all the
tools you need for this are already installed as part of Docker_ itelf.

.. code-block:: bash

    docker stack deploy --compose-file some.yml <stack_name>


These docker-compose files support pretty much everything that the ``docker-compose`` command line tool does (with the
exception of ``build``), plus at least one new one of interest ``deploy``.

As the name suggests the ``deploy`` key is concerned with how the service should run when deployed. It is found within
the definition section of a service and allows you to specify things like the number of replicas that should be run by
default.


replicas
    The number of replicas of this service desired by default

mode
    Is this a ``replicated`` or ``global`` service

resources
    Resource constraints to apply

placement
    Rules for inform the manager node how to place this services

and many others. The Docker_ `compose file documentation`_ has a lot more information as well as helpful examples.


.. note::
    You docker compose file must be of version 3.0 or above.


Controller a Docker Swarm Remotely
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

All the examples above make the assumption that you are running the Docker_ command on a manager node in the cluster,
which might not be the ideal mechanism to manage a production cluster.

The Docker_ engine does support remote control. It is just disabled by default as there are security requirements that
must be met to ensure that you lock down remote control to only those who should have it.

The full details of ensuring a secure connection is possible is best left to the experts, and details documentation for
`protecting the Docker daemon socket`_ is an excellent place to start. It details the process for sharing the Docker_
daemon socket over a secure (HTTPS) connection and enabling client certificate based authentication.

Once you do have a secure remote connection to the Docker_ socket running on one of the clusters manager nodes you can
set the ``$DOCKER_HOST`` environmental variable to ensure all Docker_ commands are directed to your cluster rather than
run locally.

.. code-block:: bash

    $ export DOCKER_HOST=tcp://<cluster ip or hostname>:2376 DOCKER_TLS_VERIFY=1
    $ docker ps  # This will now run on the specifed cluster


.. todo::

    I should also add something on secrets and config management in Docker swarm as both a pretty useful.


An Aside on Kubernetes
----------------------

Kubernetes_ has definitely emerged as a leader in the container orchestration space. It is derived from the tooling
that Google uses internally to manage services in it's clusters. It is also the foundation of Google container
management service offering with both Microsoft's Azure and Amazon's AWS have started offering their own versions.

Kubernetes_ is indeed far more flexible than Docker_ in swarm mode. However, with that flexibility comes a greater
amount of complexity. The learning curve and maintenance overheads of Kubernetes_ I think this render is less suitable
for smaller scale deployments and probably not the best technology on which to build your products in such situations.
Unless of course you have significant internal experience with it or you know that your product is going to have a
large number of development teams with a very large number of individually deployable services.

Don't get me wrong, I think Kubernetes_ is currently the best of breed when it comes to container orchestration. I just
also think it is over-kill for many situations. Perhaps the use of the hosted Kubernetes_ solutions from the various
cloud providers would be a viable option without adding too much management overhead. But to build, manage and maintain
your own Kubernetes_ cluster is not a trivial task.


*X* as a Service
----------------

*X* as a Service is term applied to a number of different offerings, perhaps originating from the term *Software as a
Service (SaaS)*. Key examples include *Platform as a Service* with perhaps the biggest supplier in this category being
Heroku_ and *Functions as a Service*, aka *serverless* with `AWS Lambda`_ as the original and most widely used
provider.

Docker_ itself, even in swarm mode could not be considered a :abbr:`PaaS (Platform as a Service)` or a
:abbr:`FaaS (Functions as a Service)`, but it does provide the foundational building blocks for them.

The aim of a ``PaaS`` is automate or abstract away the building and management of the infrastructure typically
associated with a software product. Such that product developers can focus almost entirely on their product without
having to be overly concerned about what it run it on.

There are a number ``PaaS`` offerings that target the use of Docker_ such as Deis_ which has switched to targeting
Kubernetes_ only with their latest release. Alternatively there is Flynn_ which *can* run on a Kubernetes_ cluster but
is equally at home using the simpler approach of using Docker_ itself in swarm mode. Both these systems provide a
complete ``PaaS`` system with development workflows similar to Heroku_. That is a deployment is as simple as a
``git push``. Code pushed to these platforms is built against the determined runtime automatically, e.g. a Python_
runtime is selected if a ``requirements.txt`` file is found in the root of the project. The ultimate destination of
that code being a Docker_ image, which the tool then schedules to run on one or more nodes in your cluster. Taking care
of routing and load balancing for you. Other examples in this area are: Convox_ and Tsuru_.

``FaaS`` on the otherhand provides a lower level abstraction, right down to the invidual functions, or at least to
those functions that represent the API of your product. Also often refered to by the somewhat misleading moniker
*Serverless*. ``FaaS`` is for people that have no need or want to do any real management of infrastructure, and this
fairly low level of abstraction leads to a very different approach to product architecture, with a strong tendancy
toward small, discrete functions that are independently deployable.

As with ``PaaS`` there are a number of projects that provide their own interpretation of ``Faas``. A good example is
open-faas_, which provides a number of services that can be deployed via a Docker_ swarm stackfile, or onto a
Kubernetes_ cluster. These services provide a ``FaaS`` setup similar to the combination of `AWS` Lambda`_ and
`AWS API Gateway`_. Whilst it doesn't have the breadth of functionality or integrations that are provided by some of
the commercial suppliers, it does avoid vendor lock-in and is more flexible in terms of language and runtime support.
Open-faas_ effectively supports any language or runtime that can run in a Docker_ container. Other examples in this
space include fn_ and nuclio_.



.. _`official docker registry`: https://hub.docker.com/
.. _`docker registry`: https://docs.docker.com/registry/
.. _`swarm mode`: https://docs.docker.com/engine/swarm/
.. _`compose file documentation`: https://docs.docker.com/compose/compose-file/#deploy
.. _`protecting the docker daemon socket`: https://docs.docker.com/engine/security/https/
.. _heroku: https://www.heroku.com
.. _`aws lambda`: https://aws.amazon.com/lambda/
.. _docker: https://www.docker.com
.. _open-faas: https://www.openfaas.com/
.. _kubernetes: https://kubernetes.io/
.. _`aws api gateway`: https://aws.amazon.com/api-gateway/
.. _deis: https://deis.com/
.. _flynn: https://flynn.io/
.. _python: https://www.python.org
.. _convox: https://convox.com/
.. _tsuru: https://tsuru.io/
.. _fn: https://fnproject.io/
.. _nuclio: https://nuclio.io/
