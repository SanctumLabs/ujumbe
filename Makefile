# Installs dependencies
install:
	poetry install

# Runs application
run:
	python server/server.py

# Runs the application with reload flag set
run-reload:
	uvicorn app:app --port 5000 --reload

# Runs SMS worker
run-sms-worker:
	celery -A app.worker.celery_app worker --events -l info -n ujumbe-sms-worker@%n --concurrency=5 -Q sms-queue

# Runs SMS Error worker
run-error-worker:
	celery -A app.worker.celery_app worker --events -l info -n ujumbe-dlt-worker@%n --concurrency=5 -Q sms-error-queue

# Runs Analytics worker
run-analytics-worker:
	celery -A app.worker.celery_app worker --events -l info -n ujumbe-analytics-worker@%n --concurrency=5 -Q sms-analytics-queue

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

format:
	black app

lint:
	pylint app

load-test:
	locust --config .locust.conf
