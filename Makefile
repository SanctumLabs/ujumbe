########################################################################################################################
# Setup commands
########################################################################################################################

install: # Install dependencies
	poetry install

########################################################################################################################
# Run commands
########################################################################################################################

run: #run main application
	python server/server.py

# Runs the application with reload flag set
run-reload: #run application with reload enabled
	uvicorn app:app --port 5000 --reload
.PHONY: run-reload

run-sms-received-consumer: # run sms received consumer application
	python app/workers/consumers/sms_received/__main__.py
.PHONY: run-reload-sms-received-consumer

run-sms-submitted-consumer: # runs the sms submitted consumer application
	python app/workers/consumers/sms_submitted/__main__.py
.PHONY: run-reload-sms-submitted-consumer

run-sms-sent-consumer: # runs the sms sent consumer application
	python app/workers/consumers/sms_sent/__main__.py
.PHONY: run-reload-sms-sent-consumer

run-sms-worker: # runs SMS worker
	celery -A app.worker.celery_app worker --events -l info -n ujumbe-sms-worker@%n --concurrency=5 -Q sms-queue

run-error-worker: # Runs SMS Error worker
	celery -A app.worker.celery_app worker --events -l info -n ujumbe-dlt-worker@%n --concurrency=5 -Q sms-error-queue

run-analytics-worker: # Runs Analytics worker
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

start-docker: # starts docker with all profiles set
	COMPOSE_PROFILES=database,kafka,monitoring docker compose up
.PHONY: start-docker

start-kafka: # start Kafka services
	docker compose --profile kafka up
.PHONY: start-kafka

start-monitoring: # start monitoring services
	docker compose --profile monitoring up
.PHONY: start-monitoring

start-database: # start database services
	docker compose --profile database up
.PHONY: start-database
