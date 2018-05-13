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
