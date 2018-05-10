.. _intro:

Introduction
============

I've always had an interest in education, both my parents were teachers as is my wife and consequently a fair
percentage of my circle of friends. Last year I spent much of my time training people, which is a little like
teaching. I now am much more appreciative of quite how tiring simply spending a day in front of people answering
questions and mentoring can be.

I, along with a team were brought in to re-train a number of developers in Python and Django. I say developers, they
all worked within the software development industry, just not all as developer. The first team we worked with
consisted of 4 developers, a tester and a business analyst. A trend that continued through the second and third teams
we worked with.

We were not only teaching them Python and Django but introducing modern development techniques and tooling. For
example, we introduced GIT (they previously used SVN), Test Driven Development, RESTful service design and whole
bunch of other concepts.

Now I have been a web developer for around half my life now and have worked with Python and Django for approaching 50%
of that. So working with relative newcomers to web development, even those with development experience has been a
really interesting experience. Things are not always the way you remember them from your time coming up. Knowledge that
you take for granted can seem like odd gaps in others. Whilst this is clearly not true, a few things did surprise me.

Whilst the raw technical knowledge needed to become productive in a new programming language and framework was an
interesting topic in itself, I found it was the development process itself that has left me in a rather contemplative
mood. An area that is broader than just those being trained, but also new starters and junior developers.

A lot of time is given to discussions around *best practice*. But given that this is often not well defined, can be
opinionated and changes over time how do you impart this information to those learning whilst allowing them to feel
productive quickly?

A good example is Python virtual environments. Any seasoned Python developer can easily explain why they are important
and *best practice* but ask any 2 how they manage them you are likely to get 3 different answers. From just
``virtualenv``, to ``virtualenv-wrapper``, ``pyenv`` with ``pyenv-virtualenv`` right through to the relatively new
``pipenv``. Each approach has it's pluses and minuses and each developer will have gone through a long process to hone
their particular approach. This is not something easily conveyed to new starters.

This is just one of the many, many things a learner is faced with. The overall process is much bigger. Things like
testing (TDD, BDD, Contract etc.), Continuous Integration, Continuous Deployment, Containers, Configuration Management
and Orchestration. Whilst no one would expect a new starter to know all the things in short order, they will expect
people to be able to be productive as soon a possible. Not just from the company financial point of view but for the
satisfaction of the person themselves. No one wants to feel like they cannot make a positive contribution.

Around 2010 I became aware of Heroku_, a :abbr:`PaaS (Platform as a Service)` offering, now owned by Salesforce_.
Whilst their major selling point was a supremely simple deployment system using ``git push``, what I found myself
delving into was how they did it, what their infrastructure looked like and trying to work out what a dyno_ actually
was.

It turns out that Heroku_ make extensive use of LXC_, a Linux containers implementation which helps keep running
processes isolated from each other and allows for restricting resources to each of those processes. This allowed them
to pack many more things onto each of their servers as the use of containers allowed isolation without the overhead of
a fully blown Virtual Machine.

Heroku_ was also the origin of much of the original work on `12 factor apps`_

LXC_ as it turns out was fairly difficult to get your head around and although I could make things with it, the process
was a little onerous. So I put it to bed and went back to using Vagrant_ for my local development needs.

Not long after this, another start-up with a similar offering came to my attention, dotCloud_. Amongst other things,
they had a product called Docker_. At the time, Docker_ was a fairly simple wrapper around LXC_. It worked on Linux
only (which was fine with me) but offered a *much* simpler workflow than plain LXC_.

So useful was this tool that it was eventually spun out as it's own company and the rest is history.

My personal journey with Docker_ started with the realisation that it enabled a more convenient work flow than the
Vagrant_ process I had been following previously. With much quicker start up times, and a simpler model of one
container, one process (kinda).

By this time I was already embracing the idea of `12 factor apps`_, and in particular attempting dev/prod parity by
ensuring I was using the same backing services for development as for production. A hard learnt lesson, having been
burnt a few times with bugs that only manifested in production due to, for example, stricter type checking in my
production :abbr:`RDBMS (Relational Database Management System)` than my light weight development one.

So adopting Docker_ became a natural progression of this and on the discovery of ``fig``, later adopted by Docker_ and
renamed docker-compose_ a wholesale switch was on the cards.

Skipping forwards a few years and Docker_ is now supported on all major OS platforms (Linux of course, Windows and
macOS) pretty much natively and rarely do I start a project without also creating a ``docker-compose.yml``.

The story does not end there of course, in that time the popularity of Docker_ has sky rocketed with the adoption of
the technology well beyond the lonely developer on their local machine. It has been adopted by all the major cloud
provider in one way or another as the preferred deployment artefact. Major progress has also been made on the tooling
for managing or orchestrating complex applications consisting of many docker containers.

.. _docker: https://www.docker.com
.. _heroku: https://www.heroku.com
.. _`12 factor apps`: https://12factor.net/
.. _salesforce: https://www.salesforce.com
.. _dyno: https://www.heroku.com/dynos
.. _lxc: https://linuxcontainers.org/lxc/introduction/
.. _vagrant: https://www.vagrantup.com/
.. _dotcloud: https://en.wikipedia.org/wiki/DotCloud
.. _docker-compose: https://docs.docker.com/compose/
