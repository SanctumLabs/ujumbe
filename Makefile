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

# Runs tests
test:
	PYTHONPATH=. pytest
.PHONY: test

# Runs tests with coverage
test-cover:
	PYTHONPATH=. pytest --cov=app tests/
.PHONY: test-cover

format:
	black app

lint:
	pylint app

load-test:
	locust --config .locust.conf