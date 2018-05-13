.PHONY: test update format static behave build

test:
	rind pytest

update:
	rind pip install -r /app/requirements/local.txt

format:
	rind yapf -ri -vv .
	rind isort -y -rc -vb .

static:
	rind mypy --ignore-missing-imports .

build:
	docker build -t moose/django-base .

debug:
	telnet 127.0.0.1 6899

deploy:
	# decrypt secrets
	DOCKER_SOCKET=<somewhere.com> docker stack deploy -c deployment/stack.yml base
	# remove decrypted secrets
