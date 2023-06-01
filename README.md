# Ujumbe

[![semantic-release](https://img.shields.io/badge/%20%20%F0%9F%93%A6%F0%9F%9A%80-semantic--release-e10079.svg)](https://github.com/semantic-release/semantic-release)

SMS Gateway that handles sending sms. This needs an SMTP server already setup.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Pre-requisites

Any editor of your choice can be used for this application.

1. [Python](https://www.python.org)

   This project has been built with Python 3.8. Ensure that you install this version of Python as outlined in the
   link provided [here](https://www.python.org/downloads/)

2. [Pip](https://pip.pypa.io/en/stable/)

   This is a package manager for Python applications and will be useful when handling dependencies
   for this application. Installations instructions can be found in the link int the title.

3. [Pipenv](https://pipenv.readthedocs.io/en/latest/)

   An awesome dependency management tool for Python and is highly recommended. This is the preferred
   tool of choice for this project. This allows use to separate between dev dependencies and dependencies

4. [Docker](https://www.docker.com/)

   This will be used when containerizing the application for running in a SOA(Service Oriented Architecture). This is
   used especially when deployment. Allows this application to run in any environment with minimal configuration.

First of, create a `.env` file from [.env.example](.env.example) which will contain environment variables for configurations. This file is not checked into VCS(Version Control System).

> Typically Application port will be set to a default of 5000, but if you prefer a different port to use, you can set that in the environment variable

## Installing

You will first need to install the dependencies as specified in the Pipfile file by running:

` pipenv install `

## Running the application

1. Start by first running `docker-compose up` in root of project to run services required/needed by sms-gateway
2. Run Dev server of application with `python manage.py runserver`
3. Run celery workers with `celery -A app.celery_worker.celery_app worker --events --loglevel=INFO -n sms-worker@%n --concurrency=5`

## Deployment

 Application has been built to allow for packaging into a container(a self contained application). This is made possible using [Docker](https://www.docker.com/). This allows the application to be built and run in any environment independently with very few external dependencies.

Deployment is done in 3 environments:

1. Dev

    Dev environment will ideally be used to run tests and setup for UAT.

2. UAT (or Staging)

    UAT environment will be used to test mostly by QA to ensure everything is running as expected. This is our staging environment, thus it is important that everything here matches what will happen in production.

3. Production

    Once all is well with the UAT environment (and with our souls, :D), the application is upgraded to production environment.

To run the application in a docker container use the below commands:

`docker build -t <NAME_OF_IMAGE>:<VERSION> .`
OR
`docker build -t <NAME_OF_IMAGE>:<VERSION> -f Dockerfile`
First build the image and tag it with a name, the suffix is optional, notice the dot (.)

Then now you can run the application in the container and expose ports to the host

`docker run -it -p <HOST_PORT>:4000 <NAME_OF_IMAGE>`
Run the application container binding the container port to a host port.

The host port can be whatever you like as long as it is not a reserved host port (e.g, running linux services, if on Linux). However, the container port (6000) is a must as the container exposes that port (This can be changed from the [Dockerfile](./Dockerfile))

Ideally, this will be a representation of what will run in production in a single container(pod) in a kubernetes cluster.

## Documentation

API Documentation is generated with swagger and can be accessed on the endpoint `/apidocs/` of the running application.

## Built with

- FastAPI
- Python(+3.7)
