Django Base Project
====================

A template project for Django and testing ground for a fully dockerised build environment


Prerequisites
-------------

This project uses a fully dockerised environment. As such you will need Docker_ and `Docker Compose`_ installed. There
are also a number of helpers within the ``Makefile`` so it would be useful, but not essential to have a copy of
``Make`` installed.

You should also have a recent copy of Rind_ installed somewhere on the path


Getting Started
---------------

Assuming you have `Docker Compose`_ installed the entire build environment can be started with:

.. code-block:: bash

	docker-compose up


This will start the PostgreSQL_ database server, a Django application server and a Sphinx_ documentation service.

The Django application service will reload automatically (after a few seconds) when changes are made within ``/app``
and you can access the server using `localhost:8000`_.

The Sphinx_ documentation service will also automatically rebuild the documentation on change and is available on
`localhost:8080`_



Development Tasks
-----------------

To make running everything inside a Docker_ container slightly less painful the project contains a ``Makefile`` with a
number of targets, described below.


Running Tests
+++++++++++++


Tests are run with `py.test`_. We are using the `pytest-isort` and `pytest-flake8` plugins for static analysis.
You can run the full test suite with:

.. code-block:: bash

	make test


Updating the Virtual Environment
++++++++++++++++++++++++++++++++

The virtual environment resides within the Django app Docker_ container, so when you add or change requirements
(found in ``/app/requirements/*.txt``) you need to do so inside the container:

.. code-block:: bash

	make update


Format Python
+++++++++++++

This project provides yapf_ to automatically format Python code to our (``pep8`` derived) standard and isort to ensure
that imports are sorted nicely. To automatically apply formatting changes:

.. code-block:: bash

	make format


Static Analysis
+++++++++++++++

MyPy_ has been included to do static type checking. To run mypy_:

.. code-block:: bash

	make static


Building a Docker Image
+++++++++++++++++++++++

.. code-block:: bash

	make build


Brain Dump Log
--------------

2017-12-19:
	The ``Makefile`` approach to running stuff in the container is a bit cumbersome. In particular, where I want to
	pass through command line options. e.g. having a Django management command target is not really usable unless I
	specify each one separately. Not a good solution. Could something else be used which is more flexible but still
	doesn't require Python to be installed.  Perhaps a simple cli compiled with nuitka?

2017-12-19:
	I tried writing something and compiling with Nuitka, however the standalone compilation does not statically
	compile in libraries, you would need to copy them all around as well which is not ideal.

	So I wrote something in Go. This does compile to a single, statically linked executable and allows cross compiling,
	which is nice. rapyd_ (Run A Python in Docker) is the tool and it basically takes all command line args and runs
	them inside the docker container instead.  It is a seriously simplistic but appears to work.

	I also managed (with a little tweaking) to get the whole setup running in PyCharm, including the debugger. Which
	does remind me that we probably need a way of running a debugger when not using PyCharm.

2018-01-03:
	Using docker compose for the web server I think it means I can just use ``pudb`` for example, as long as I assign
	an interactive terminal to the ``web`` service.

	I also wonder if I should start doing type annotations and add a ``mypy`` target. I don't think that Django yet has
	annotation or that any have been added to ``typeshed``, which is a bit of a shame.

2018-01-04:
	So ``pudb`` wasn't quite as straight forward as I thought. Setting ``stdin_open: true`` and ``tty: true`` in the
	docker compose file and then trying to ``set_trace`` in my code gave a bunch of unexpected error messages. However
	it seems ``pudb`` has an awesome remote debugger built in that can just be accessed using a telnet session.
	Horribly insecure in the real world but perfect inside a docker container running locally for development.

	``from pudb.remote import set_trace; set_trace(term_size=(160, 40), host='0.0.0.0', port=6899)``

	Then on the host machine:	``telnet 127.0.0.1 6899``

	Just make sure you forward port ``6899`` to your local machine in the ``docker-compose.yaml``. I've added a make
	target for this.
2018-??-??
	So I wanted to add some more features to rapyd_ and I wanted to know how docker-compose_ did it. Turns out that my
	belief that on adoption of fig, the Docker people didn't actually re-write it in Go. It's still Python. Which makes
	me question how they build a single standalone executable...

	Turns out they use PyInstaller. Which again blows my understanding of something. I had thought PyInstaller a tool
	to build installers for Python apps, like a ``setup.exe/msi`` for Windows etc. Turns out it is much more like
	Nuitka. So I gave it a shot and low and behold rind_ was born and although it doesn't allow cross compilation, I do
	have ready access to both a Linux machine and a Mac, so not the end of the world.
2018-05-05:
	I'm going to have to replace or at least augment envparse with something to look in docker secrets
	(``/run/secrets/<name>``) and docker config (``/<name>`` by default) and finally to look and environmental
	variables.  I'd also like the DB url thing as separate components for each is annoying.

	envparse does support URLs, and will return an instance of ``urllib.parse.ParseResult`` if a URL is specified in
	the mathcing environmental variable. Interesting ``envparse`` does not attempt to parse/coerce any value passed in
	as the ``default``. So you can't just pass the a URL string as the default as all you will get is the same string
	out again if the environmental variable is not set. Not ideal, I can probably live with it, but implementing a
	simply replacement might be good, as I can included Dcoker_ secret and config lookup as well as environmental
	variables. With some kind of hierarchy and possibly a ``url`` variant for Django DBs.

	I should really start thinking about front end matters. Although I am kind of in favour of separating them.

	I have added a dpeloyment folder now, in here is a ``stack.yml`` - Same format as the ``docker-compose.yml`` but
	just the stuff needed to deploy the Django application to a docker_ swarm.  I have also created folders for secrets
	and config.  For the secrets I am going to have to do some kind of encryption to ensure the contents are protected,
	and then wrap decrypt, deploy, re-encrypt into a ``Makefile`` target. I've used ansible vault for this sort of
	thing before, but it seems odd to use that for this when I'm not using anythinh else from Ansible. Maybe straight
	PGP makes sense, or perhaps even keybase as that seems to have become the defacto way to share password as CC.

	There has been a fair amount of talk recently about testing in a Docker_ world. My previous CI approach was to
	simply setup the virtualenv, run tests with Pytest and then build the docker image. This isn't really testing the
	code within a docker image though, so the next was to have a pre-build base image into which the code is mounted
	and tox is run to build it all out and test it.  This *is* within a container, but **not** one that represents the
	actual production deployment.  So we have been talking about the CI building a production ready docker image, with
	no separation in installed dependancies with the development environment. e.g. all the testing and potentially
	debugging tools are included in the images that gets shipped to production. CI becomes build image, test in image,
	ship. It does mean that the final image has tests and testing tools included but it mean that when you run tests,
	you are testing the real thing that is actually going to get deployed.

.. _docker: https://www.docker.com/
.. _`docker compose`: https://docs.docker.com/compose/install/
.. _rapyd: https://github.com/a-musing-moose/rapyd
.. _rind: https://github.com/a-musing-moose/rind
.. _postgresql: https://www.postgresql.org/
.. _sphinx: http://www.sphinx-doc.org/en/stable/
.. _`localhost:8000`: http://localhost:8000
.. _`localhost:8080`: http://localhost:8080
.. _`py.test`: https://pytest-django.readthedocs.io/en/latest/
.. _yapf: https://github.com/google/yapf
.. _mypy: http://mypy-lang.org/
.. _behave: https://pythonhosted.org/behave/
