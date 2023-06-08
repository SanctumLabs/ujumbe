########################################################################################################################
# Setup commands
########################################################################################################################

# Installs dependencies
install:
	poetry install

########################################################################################################################
# Run commands
########################################################################################################################

# Runs application
run:
	python server/server.py

# Runs the application with reload flag set
run-reload:
	uvicorn app:app --port 5000 --reload
.PHONY: run-reload

# Runs the sms received consumer application
run-sms-received-consumer:
	python app/workers/consumers/sms_received/__main__.py
.PHONY: run-reload-sms-received-consumer

# Runs the sms submitted consumer application
run-sms-submitted-consumer:
	python app/workers/consumers/sms_submitted/__main__.py
.PHONY: run-reload-sms-submitted-consumer

# Runs the sms sent consumer application
run-sms-sent-consumer:
	python app/workers/consumers/sms_sent/__main__.py
.PHONY: run-reload-sms-sent-consumer

# Runs SMS worker
run-sms-worker:
	celery -A app.worker.celery_app worker --events -l info -n ujumbe-sms-worker@%n --concurrency=5 -Q sms-queue

# Runs SMS Error worker
run-error-worker:
	celery -A app.worker.celery_app worker --events -l info -n ujumbe-dlt-worker@%n --concurrency=5 -Q sms-error-queue

# Runs Analytics worker
run-analytics-worker:
	celery -A app.worker.celery_app worker --events -l info -n ujumbe-analytics-worker@%n --concurrency=5 -Q sms-analytics-queue

########################################################################################################################
# Testing commands
########################################################################################################################

# Runs all tests tests
test:
	PYTHONPATH=. pytest
.PHONY: test

# Runs integration tests
test-integration:
	PYTHONPATH=. pytest tests/integration
.PHONY: test-integration

# Runs integration tests with coverage
test-integration-cover:
	PYTHONPATH=. pytest --cov=app tests/integration/
.PHONY: test-integration-cover

# Runs end to end tests
test-e2e:
	PYTHONPATH=. pytest tests/e2e
.PHONY: test-e2e

# Runs e2e tests with coverage
test-e2e-cover:
	PYTHONPATH=. pytest --cov=app tests/e2e/
.PHONY: test-e2e-cover

# Runs unit tests
test-unit:
	PYTHONPATH=. pytest tests/unit
.PHONY: test-unit

# Runs unit tests with coverage
test-unit-cover:
	PYTHONPATH=. pytest --cov=app tests/unit/
.PHONY: test-unit-cover

# Runs all tests with coverage
test-cover:
	PYTHONPATH=. pytest --cov=app tests/
.PHONY: test-cover

load-test:
	locust --config .locust.conf

########################################################################################################################
# Lint and formatting commands
########################################################################################################################
format:
	black app

lint:
	pylint app

########################################################################################################################
# Generation and build commands
########################################################################################################################

# Builds the buf module
buf-build:
	buf build
.PHONY: buf-build

# updates the buf module
buf-update:
	buf mod update
.PHONY: buf-update

# generates protobuf messages
buf-generate:
	buf generate
.PHONY: buf-generate

########################################################################################################################
# Migration commands
########################################################################################################################

migrate-up:
	alembic upgrade head
.PHONY: migrate-up

migrate-down:
	alembic downgrade base
.PHONY: migrate-down

migrate-revision:
	alembic revision --autogenerate -m "$(ARGS)"
.PHONY: migrate-revision

########################################################################################################################
# DOCKER commands
########################################################################################################################

start-docker:
	COMPOSE_PROFILES=database,kafka,monitoring docker compose up
.PHONY: start-docker

# Start Kafka services
start-kafka:
	docker compose --profile kafka up
.PHONY: start-kafka

# Start monitoring services
start-monitoring:
	docker compose --profile monitoring up
.PHONY: start-monitoring

# Start database services
start-database:
	docker compose --profile database up
.PHONY: start-database
