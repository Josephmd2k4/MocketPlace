ARG PYTHON_VERSION=3.11-slim

FROM python:${PYTHON_VERSION}

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN mkdir -p /code

WORKDIR /code

COPY requirements.txt /tmp/requirements.txt
RUN set -ex && \
    pip install --upgrade pip && \
    pip install -r /tmp/requirements.txt && \
    rm -rf /root/.cache/
COPY . /code

ENV SECRET_KEY "h2VAo0XK4odJTzt5dngKCtlidI2lftVSZ2UUUTxxQ0m45ekixG"
RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["daphne","-b","0.0.0.0","-p","8000","MocketPlace.asgi:application"]
