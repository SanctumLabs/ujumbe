# Ujumbe

[![semantic-release](https://img.shields.io/badge/%20%20%F0%9F%93%A6%F0%9F%9A%80-semantic--release-e10079.svg)](https://github.com/semantic-release/semantic-release)

SMS Gateway that handles sending sms. This needs an SMTP server already setup.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing
purposes. See deployment for notes on how to deploy the project on a live system.

### Pre-requisites

Any editor of your choice can be used for this application.

1. [Python](https://www.python.org)

   This project has been built with Python 3.8. Ensure that you install this version of Python as outlined in the
   link provided [here](https://www.python.org/downloads/)

2. [Pip](https://pip.pypa.io/en/stable/)

   This is a package manager for Python applications and will be useful when handling dependencies
   for this application. Installations instructions can be found in the link int the title.

3. [Poetry](https://python-poetry.org/)

   An awesome dependency management tool for Python and is highly recommended. This is the preferred
   tool of choice for this project. This allows use to separate between dev dependencies and dependencies

4. [Docker](https://www.docker.com/)

   This will be used when containerizing the application for running in a SOA(Service Oriented Architecture). This is
   used especially when deployment. Allows this application to run in any environment with minimal configuration.

5. [Twilio Account](https://www.twilio.com/en-us)

   Twilio is the 3rd Party SMS client that is used to actually send out SMS messages. In order to send these messages
   with this application. One will need to setup a Twilio account and obtain the account sid, auth token and message sid
   and set them in the values: `TWILIO_ACCOUNT_SID` and `TWILIO_AUTH_TOKEN` and optionally, `TWILIO_MESSAGE_SID` as
   specified in the [.env.example](.env.example) file. Twilio has been disabled by default and stubbed out in the
   application, but can be enabled using the `TWILIO_ENABLED` environment variable. Setting it to `True` enables using
   Twilio to send out the SMS messages.

6. [Sentry Account](https://sentry.io/)

   Sentry is used for error tracking and monitoring and can be used in this application. Once one creates an account
   with Sentry, proceed to add the sentry DSN value in the [.env.example](.env.example) file as the `SENTRY_DSN`
   environment variable. Other values have been reasonably set, such as `SENTRY_TRACES_SAMPLE_RATE`
   and `SENTRY_DEBUG_ENABLED`, but can be modified. Additionally, Sentry is disabled by default with the environment
   variable `SENTRY_DEBUG_ENABLED`, but should be enabled in a production setting, if one wants to enable this during
   development, you can set this environment variable to `True`

First of, create a `.env` file from [.env.example](.env.example) which will contain environment variables for
configurations. This file is not checked into VCS(Version Control System).

> Typically Application port will be set to a default of 5000, but if you prefer a different port to use, you can set
> that in the environment variable

## Installing

You will first need to install the dependencies as specified in the [pyproject](pyproject.toml) file by running:

There are some dependencies that are not on PyPI and therefore some additional setup will be required. First step is to
add a source/repository in order for poetry to install them.

```shell
poetry --source add gitlab-pypi https://gitlab.com/api/v4/projects/47231151/packages/pypi/simple/
```

Since, the repository requires authentication, configure credentials for it:

```shell
poetry config http-basic.gitlab-pypi __token__ <GITLAB_PERSONAL_ACCESS_TOKEN>
```

> Your `GITLAB_PERSONAL_ACCESS_TOKEN>` is your Gitlab Personal Access token, more
> information [here](https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html) that has the scope
> of `read packages`. This will allow access to the package on Gitlab.

Once that is done dependencies can be added to the project from this source:

```shell
poetry add --source gitlab-pypi <PACKAGE_NAME>
```

> Where `<PACKAGE_NAME>` is the name of the packge to install from the repository

Now, you can run the below command

```shell
poetry install
```

Or

```shell
make install
```

> This is a convenience wrapper around `poetry install`

The [Makefile](Makefile) contains commands that are used in the project.

## Running the application

In order to run the application, we need to first run docker containers specified in
the [docker compose file](docker-compose.yml). This specifies services that are used by the application while it runs
such as:

1. [Kafka](https://kafka.apache.org/)
2. [Kafka Schema Registry](https://docs.confluent.io/platform/current/schema-registry/index.html)
3. [Zookeeper](https://zookeeper.apache.org/)
4. [Postgres](https://www.postgresql.org/)
5. [Zipkin](https://zipkin.io/)
6. [Grafana](https://grafana.com/)
7. [Redis](https://redis.io/)

To get more details about the architecture of the project, consult the documentation as
specified [here](docs/Architecture.md).

Steps to run the project include:

1. Start by first running the docker containers of the above services

   These services have been split into different profiles as stated in the
   doc [here](https://docs.docker.com/compose/profiles/). In order to run all the services at once, one can use make to
   conveniently run all the services:

   ```shell
    make start-docker
   ```

2. Next, run migration script to setup the database schema:

   ```shell
   make migrate-up
   ```

3. Next, run the application with:

   ```shell
    make run
    ```

   Or

    ```shell
    make run-reload
    ```

   > Runs the application watching for changes in the [app](app) directory

4. Next, run the consumer workers/listeners which consume events from Kafka:

   ```shell
   make run-sms-received-consumer
   ```

   > Runs the SMS received consumer

   on a different terminal, run the SMS submitted consumer:

   ```shell
   make run-sms-submitted-consumer
   ```

   on a different terminal, run the SMS Sent consumer:

   ```shell
   make run-sms-sent-consumer
   ```

To run the application in a docker container use the below commands:

`docker build -t <NAME_OF_IMAGE>:<VERSION> .`
OR
`docker build -t <NAME_OF_IMAGE>:<VERSION> -f Dockerfile`
First build the image and tag it with a name, the suffix is optional, notice the dot (.)

Then now you can run the application in the container and expose ports to the host

`docker run -it -p <HOST_PORT>:4000 <NAME_OF_IMAGE>`
Run the application container binding the container port to a host port.

The host port can be whatever you like as long as it is not a reserved host port (e.g, running linux services, if on
Linux). However, the container port (6000) is a must as the container exposes that port (This can be changed from
the [Dockerfile](./Dockerfile))

Ideally, this will be a representation of what will run in production in a single container(pod) in a kubernetes
cluster.

## Running tests

The application tests can be found [here](tests) split into sub folders
for [unit tests](tests/unit), [integration tests](tests/integration) and [end-to-end tests](tests/e2e). These tests can
be run like below:

```shell
make test-unit
```

> Runs unit tests

```shell
make test-integration
```

> Runs integration tests

```shell
make test-e2e
```

> Runs end-to-end tests
> Note, that running e2e tests is a little more complicated, as it involves spinning up docker containers, This is
> documented in the [testing doc](docs/Testing.md)

```shell
make test
```

> Runs all the tests

## API Documentation

API Documentation is generated with OpenAPI and can be accessed on the URL <http://127.0.0.1:5000/docs> while running
the
application locally.

## Built with

This application has been built with the following tools:

- [Python +3.10](https://www.python.org/). Programming Language
- [FastAPI](https://fastapi.tiangolo.com/). Web framework
- [dependency-injector](https://github.com/ets-labs/python-dependency-injector). Dependency injection library
- [tenacity](https://tenacity.readthedocs.io/en/latest/). Retrying library
- [Confluent kafka](https://developer.confluent.io/get-started/python/#introduction). Kafka client library
