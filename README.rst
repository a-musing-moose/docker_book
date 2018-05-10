A Deep Dive into Docker for Development
=======================================

Just getting started in development in any language attracts a significant learning curve. Ensuring what you are doing
along the way is best practice is even more difficult.

This applies not only to those learning a new language but also to those new to an established project or wishing to
start one that others can get up to speed on ASAP.

A Deep Dive into Docker for Development is my journey to adapting my somewhat opinionated Python_ workflow to a world
in which Docker_ exists.

This repository contains the draft of the book, currently in progress. It has no release date and may never be
completed. But it is all here in the open and licenced under a CC-BY-SA_ licence.

Getting Started
---------------

This book is being written in RST using Sphinx_. However, you don't need to know much about Sphinx_ or Python_ to get
it up and running. You will however need Docker_ and docker-compose_ installed. Once installed you can run:

.. code-block:: bash

    docker-compose up


This will start a webserver (on http://127.0.0.1:8000) that will monitor the source code and re-build when it changes.


.. _docker: https://www.docker.com/
.. _python: https://www.python.org
.. _cc-by-sa: LICENCE.rst
.. _sphinx: http://www.sphinx-doc.org/
.. _docker-compose: https://docs.docker.com/compose/install/
