> **Status: Proposed. Discovery output dated 2026-10-07; not accepted architecture.** Describes the code as inspected on that date and a proposal for its replacement. Decisions are tracked in the ADR index and open-question log.

# ujumbe: as-is design (SMS gateway)

Repo `ujumbe` (GitHub SanctumLabs/ujumbe), `develop` @ `6b097ec` (2026-10-01). Product code was last changed in
January 2024 (`git log -- app`); everything since is Dependabot bumps. Local history is shallow (99 commits).
Method: every claim below was read in code. Items marked **Run** were executed in a scratch copy (Python 3.11, locked
versions, psycopg2 swapped for psycopg2-binary because the sandbox has no `Python.h`).

## 1. Tech stack and versions

| Concern | Choice | Version (poetry.lock) | Note |
|---|---|---|---|
| Language | Python | `^3.10` declared (`pyproject.toml:8`); CI runs 3.10 (`.github/workflows/lint.yml:17`); README says 3.8 and "+3.10"; Dockerfile says 3.8.6 | Python 3.10 reaches end of life this month (Oct 2026) |
| REST | FastAPI + Starlette + uvicorn | 0.109.1 / 0.35.1 / 0.20.0 | `uvicorn[stadard]` typo in extras (`pyproject.toml:10`) |
| Validation/settings | pydantic **v1** (`BaseSettings`, `validator`, `GenericModel`) | 1.10.13 | v1 is end of life and cannot run on 3.14 |
| DI | dependency-injector | 4.41.0 | declarative containers wired to FastAPI |
| Broker | Kafka via confluent-kafka + schema registry, protobuf | 2.0.2 (Jan 2023) / protobuf 5.29.6 | consumers are hand-rolled poll loops |
| DB | PostgreSQL, SQLAlchemy 2.0.7 sync, psycopg2 (source build), Alembic 1.10 | | audit trigger SQL under `migrations/sql` |
| Provider | Twilio SDK | 7.17.0 | EOL major (current is 9.x) |
| Logging | loguru 0.6 | | six sinks all to stdout |
| Dead | Celery 5.2 + redis (`app/celery_app.py`, `app/tasks`) | | not wired to anything that works |
| Test | pytest 9, faker, testcontainers 0.0.1rc1, docker-py 6.0.1 | | see section 9 |
| Lint | pylint (CI/`make lint`), black, flake8, mypy declared | | see section 10 |

Size: 3,787 lines of non-generated app Python, 2,894 lines of tests.

## 2. Repository structure and layering

```
server/server.py            uvicorn launcher ("app:app", port 5000)
app/__init__.py             FastAPI app, container wiring, 2 middlewares, exception handlers
app/api/                    REST: sms/routes.py (POST /api/v1/sms/), monitoring/routes.py (GET /healthz), DTOs
app/domain/                 entities (Sms, PhoneNumber, Message, SmsResponse, SmsDeliveryStatus...) and use cases
  domain/sms/               CreateSmsService, SubmitSmsService, SendSmsService, repository port, exceptions
app/core/                   generic DDD scaffolding (Entity, UniqueId, Repository, Producer, Consumer, SmsService ports)
app/services/               "adapters": Kafka event producers/consumers per event type + UjumbeSmsService (provider wrapper)
app/infra/                  kafka (producers, consumers, serializers, registry), sms/sms_client.py (Twilio), database client,
                            logger, middleware, exception handlers
app/database/               SQLAlchemy models, mapper, repositories
app/workers/consumers/      two while-True worker entry points: sms_received, sms_submitted
app/messages/events/v1/     data.proto, events.proto (+ checked-in generated *_pb2.py); app/app/messages/... is a stray duplicate
app/config/di/              dependency-injector containers; app/settings.py pydantic v1 settings
migrations/                 Alembic: audit schema/trigger + initial tables
docker/, docker-compose.yml dev infra only (Postgres, 3x Kafka + ZK, schema registry, Kafka UI, Zipkin, Prometheus, Grafana)
tests/{unit,integration,e2e}  e2e is empty
```

Layering is nominally hexagonal (domain / services / infra) but leaks: the domain `SmsResponse` and `SmsResponse` DB
model are Twilio's response shape (`app/domain/entities/sms_response.py:21-35`, `app/database/models/sms_response_model.py:20-101`);
`app/services/*_producer.py` build protobuf messages and sit between domain and infra; use cases depend on
`Producer`/`Consumer`/`SmsService` ports in `app/core/infra` (good), but DI containers instantiate Twilio, Kafka
and DB directly in `app/config/di/gateways_container.py`.

## 3. Domain model (what exists)

- `Sms` (`app/domain/entities/sms.py:14-62`): pydantic model mixed with a dataclass `Entity`; fields `id`, `recipient`,
  `message`, `sender?`, `status`, `response?`. `id = Entity.next_id()` at class level (line 20) is evaluated once at import,
  so all instances share one id (**Run**, finding UJU-008).
- `PhoneNumber` validates with `phonenumbers.parse(x, None)` + `is_valid_number` but stores the raw string
  (`app/domain/entities/phone_number.py:11-14`, `app/utils/validators.py:4-6`). **Run**: `"+254 700 000 000"` and `"+254700000000\n"` accepted
  verbatim; `"0700000000"` raises `NumberParseException` (not `ValueError`).
- `Message`: rejects `len(value) >= 435` characters (`message.py:5,14`); 435 itself is rejected; no encoding awareness.
- `SmsDeliveryStatus` (`sms_status.py`): ACCEPTED, SCHEDULED, CANCELED, QUEUED, SENDING, SENT, FAILED, DELIVERED,
  UNDELIVERED, RECEIVING, READ, PENDING, UNKNOWN (Twilio's vocabulary plus two). `_missing_` maps anything unknown to UNKNOWN.
  No transition rules anywhere.
- `SmsResponse`/`SmsDate`/`SmsPrice`/`SmsType`: Twilio response mirror. `SmsDate.__post_init__` compares created/sent/updated
  datetimes (`sms_date.py:40-48`).
- Value objects and entities are frozen dataclasses combined with pydantic `BaseModel` (`SmsResponse` is
  `@dataclass(frozen=True, kw_only=True)` on a `BaseModel`), which works by accident on pydantic v1.

## 4. Data model (PostgreSQL)

`sms` (`app/database/models/sms_model.py:17-47`, migration `0ad6b839a7f9`): `id serial pk`, `identifier text unique`
(nanoid), `sender not null`, `recipient not null`, `message not null`, `delivery_status` native PG enum, `created_at`
(indexed), `updated_at`, `deleted_at` (soft delete, never filtered), `updated_by`; unique
`(sender, recipient, message)` (`sms_sender_recipient_message_constraint`).
`sms_responses`: provider response copy (account_sid, `sid` unique, dates NOT NULL, `num_media`, `num_segments`, `price`
float, `currency`, `subresource_uris` JSON, `uri`, `messaging_service_sid`, `error_code`, `error_message`,
`delivery_status`, FK `sms_id` -> `sms.id`, no index on the FK). Relationship `sms.response` is scalar although the
schema permits many responses per sms.
`audit.log` + trigger `audit.audit_table('sms')` and `('sms_responses')`: every row change, full row JSON and the
SQL text of the client query are copied into `audit.log` (`migrations/sql/audit_log.sql:118,193`, migration lines 219-220).
PII (recipient number, message body) therefore exists in three places: base table, `audit.log.original`/`diff`, `client_query`.
No tenant, provider, idempotency-key, correlation or consent columns.

## 5. Messaging surfaces

### REST (FastAPI)
Only two routes (**Run**, `/openapi.json`): `POST /api/v1/sms/` and `GET /healthz`.
`POST` body `{sender?, recipient, message}` (`app/api/sms/dto.py:9-25`). No auth, no idempotency key, no versioning beyond path.
Responses are `ApiResponse{status, data, message}`; failures that are `AppException` return **HTTP 200** with body
`status: 500` (`app/api/sms/routes.py:47-51`); other failures (bad phone, over-long message, publish failure) return HTTP 500
`Internal server error` because only `AppException` is caught and `SubmitSmsException`/`CreateSmsException` do not extend it
(**Run**). Success says "Sms sent out successfully" although the request was only accepted for asynchronous processing, and no
message id is returned. `BulkSmsRequestDto` is unused. `/healthz` is a constant 200 (no dependency check). `docs_url` is enabled by default.

### Kafka
Topics from settings (`app/settings.py:77-84`): `sms_received_topic`, `sms_submitted_topic`, `sms_sent_topic`
(+ group ids). Value is protobuf with schema registry (Confluent wire format), key is always `None`
(`ProducerMessage(topic, value)`, `proto_producer.py:39`). Events (`app/messages/events/v1/events.proto`): `SmsReceived`,
`SmsSubmitted`, `SmsSent`, each wrapping `Sms{id, sender?, recipient, message, status, response?}`. No envelope: no
correlation id, tenant, occurred-at, schema version beyond the package `v1`, idempotency key or trace context.
`SmsStatus` enum zero value is `ACCEPTED` (`data.proto:54-55`), no `UNSPECIFIED`. `SmsResponse` carries `map<string, Any> subresource_uris`
and `optional float price`.
`SmsSent` is published after `send()` returns and carries the pre-send payload with status forced to `SENT`
(`app/services/sms_sent_producer.py:29-40`); nothing consumes it (the `sms_sent` worker referenced by the Makefile/README does not exist).

### gRPC
None. `buf.yaml`/`buf.gen.yaml` exist for protobuf message generation only (remote plugin `buf.build/protocolbuffers/plugins/python`, a
deprecated path; `buf` is not installed here so `buf generate` was not run). `server/` is just the uvicorn launcher.

### Inbound provider callbacks / inbound SMS
None. No webhook route, no signature verification, no `status_callback` passed when creating the message
(`app/infra/sms/sms_client.py:61-72`), no inbound (MO) handling although `SmsType.INBOUND` exists.

## 6. Main flows

### Flow A: submit (as implemented)
1. Client `POST /api/v1/sms/`. Route (an `async def`) builds `Sms.from_dict` (new id is the shared class-level id) and calls
   `SubmitSmsService.execute(sms)` synchronously (`routes.py:23,42`).
2. `SubmitSmsService` -> `SmsReceivedProducer.publish_message` -> tenacity `@retry` (3 attempts, 3-5 s sleeps, blocking)
   -> `KafkaProtoProducer.produce` -> `SerializingProducer.produce` then `flush()` with no timeout
   (`proto_producer.py:36-43`). Delivery result is only logged by the callback; `flush()` returns regardless. `MSG_SIZE_TOO_LARGE`
   is logged and swallowed (`proto_producer.py:47-50`).
3. API returns 200 "Sms sent out successfully".

### Flow B: received worker (`app/workers/consumers/sms_received/__main__.py`)
`while True`: poll -> deserialize -> build `Sms` (requires sender) -> `CreateSmsService.execute`
(insert row + commit, then publish `SmsSubmitted`, `create_sms.py:25-26`) -> publish `SmsSubmitted` **again** from the worker (line 39,
issue #68) -> `commit()` (broken, issue #69). Any exception is logged and the loop continues; auto-commit is on, so the record is
silently skipped. Persist uses `identifier` unique, so a second SMS from the same API process (same shared id) fails here and is dropped.

### Flow C: submitted worker (`.../sms_submitted/__main__.py`)
poll -> `SendSmsService.execute` -> `UjumbeSmsService.send` -> `SmsClient.send` (Twilio `messages.create`, no timeout; sender ->
`from_`, no sender -> `messaging_service_sid`) -> map response (crashes when Twilio returns `date_sent=None`, **Run**) -> insert
`sms_responses` row -> publish `SmsSent` -> `commit()`. The `sms` row status is never updated. A crash anywhere after Twilio accepts
the message produces a duplicate send on redelivery (no claim state, no provider idempotency, no dedupe).

### Flow D: delivery callback
Documented only (`docs/send_sms_flow.puml:59-67`). Not implemented (issue #71, stale PR #11).

## 7. Provider plug-in model (how it actually works)

- Port: `SmsService.send(sms)` (`app/core/infra/sms_service.py`) returning the Twilio-shaped `SmsResponse`.
- One implementation `UjumbeSmsService` (`app/services/sms_service.py`) wrapping the concrete Twilio `SmsClient`; the DI
  container constructs exactly one `SmsClient` singleton (`gateways_container.py:32-40`). `Client(account_sid, auth_token)` is built eagerly
  and raises `TwilioException` for empty credentials even when `TWILIO_ENABLED=False` (**Run**).
- Adding a provider today means: new client class, new `SmsService` implementation that re-implements the Twilio-to-`SmsResponse`
  mapping, a new DI wiring edit; there is no registry, selection key, routing table, fallback, per-provider rate limit, health
  state, capability model or credential store. Credentials are plain-`str` env settings (`settings.py:38-42`), no rotation, no secret manager.
- Stub mode is the default: `TWILIO_ENABLED=False` returns a fake successful response (status `sent`) generated with `faker`, a
  **dev-only** dependency (`sms_client.py:6,99-133`, `pyproject.toml` dev group), so the default deployment "sends" nothing and reports success, and a
  production install without dev dependencies cannot import the module.

## 8. Configuration, deployment, CI

- Settings: pydantic v1 `BaseSettings` classes instantiated at import. `DatabaseSettings.db_url` is an f-string evaluated at class
  creation, so `DB_HOST`/`DB_USERNAME` etc. never reach it (**Run**: with `DB_HOST=db.prod` the URL stays `localhost`); Alembic uses it
  (`migrations/env.py:13,89`) so `make migrate-up` hits the defaults unless `-x db_url=` is given. Defaults include credentials
  (`ujumbe-password`, SASL `ujumbe/ujumbe`). Kafka security settings are defined (`settings.py:72-75`) but never passed into the Kafka
  configs by DI (`kafka_container.py:25-63`); and when they would be, the code sets `sasl.username` to the **password**
  (`consumers/__init__.py:37`, `producers/__init__.py:34`). `.env.example` names do not match settings (`DB_DRIVER`, `KAFKA_SASL_MECHANISM`;
  `TWILIO_MESSAGING_SERVICE_SID` missing).
- Container: `Dockerfile` is `python:3.8.6-alpine3.11` + pipenv + `gunicorn config/gunicorn_config.py wsgi:app`; none of those files exist.
  No worker images, no non-root user, no healthcheck. `docker-compose.yml` is dev infra only (PLAINTEXT Kafka, anonymous Grafana admin, fixed DB password).
- Makefile targets reference missing things: `app/workers/consumers/sms_sent/__main__.py`, `app.worker.celery_app`, `.locust.conf`.
  `make lint` is `pylint app`; the black config lives in a file named `.toml` so black ignores it.
- CI: one workflow `lint.yml` (push): `pip install poetry && poetry install && make lint` on 3.10. It fails on every recent `develop` push
  (runs #146, #148, #150, #153, #154) at `poetry install` with "No file/folder found for package ujumbe" (no package dir) before
  reaching pylint. There is no test job, no build, no image scan, no migration check. CodeQL and Dependabot are the only green checks.
  `.releaserc.json` releases from branch `production` which does not exist.

## 9. Observability and operations
- Logging (`app/infra/logger.py:14-85`): six loguru sinks, all `sys.stdout` unless `ENVIRONMENT=local`; each record is printed once per
  sink whose level <= record level (**Run**: ERROR printed 5x, INFO 3x). Plain text, coloured, no JSON, no correlation id.
- No metrics, no tracing, Sentry settings never initialised (no `sentry_sdk` import). `docker/monitoring` holds Kafka/JVM dashboards only.
- `/healthz` is static. Workers have no health, no signal handling, never call `close()`.
- PII: recipient numbers and full message bodies are logged by f-string of the entity at INFO and ERROR in nearly every module
  (`sms_service.py:28,59-60`, `sms_client.py:59,97-100`, workers line 36, `routes.py:48`, `sms_repository.py:33`), and exception messages embed the body
  (`Message.__post_init__`, `SmsSendingException`).

## 10. Tests and linters: measured reality (Run)

Environment: Python 3.11.17, versions from `poetry.lock`, psycopg2 replaced with psycopg2-binary.
- `poetry install --with dev --no-root` on 3.13: fails building `gevent 23.9.1` (Cython `long` undeclared); on 3.11: fails building `psycopg2 2.9.6`
  from source (needs `Python.h`/libpq headers; the project depends on the source package, not `-binary`). `cffi 1.15.1` has no wheels for 3.12+.
  Plain `poetry install` (what CI does) additionally fails with "No file/folder found for package ujumbe".
- `pytest tests/unit`: **10 failed, 57 passed, 2 skipped**.
  - 8 API tests: `tests/__init__.py:28` builds `AppSettings(environment="test", sentry_debug_enabled=False, ...)`; those fields live on
    nested `SentrySettings`, pydantic v1 rejects extras (`extra fields not permitted`). `setUp` fails for every API test.
  - `test_monitoring_route`: `@pytest.mark.anyio` on a `unittest.TestCase`; `setUp` never runs, `async_client` missing.
  - `test_sms_received_producer::test_throws_exception_when_there_is_an_error_producing_message`: expects one `produce` call, tenacity makes three
    and the test takes ~6 s of real sleep.
  - 2 skipped: a worker test ("runs forever") and an API test ("failure to mock side effect").
- `pytest tests/integration`: 22 errors. Besides the sandbox having no Docker daemon, docker-py 6.0.1 fails with
  `Not supported URL scheme http+docker` against the locked `requests 2.33.0` (docker-py < 7.1 is incompatible with requests >= 2.32), and
  testcontainers 0.0.1rc1 teardown raises `AttributeError: _container`. Two Kafka integration tests are skipped unconditionally.
  Integration DB tests build the schema with `create_all`, not Alembic, so migrations are never exercised.
- `make lint` (`pylint app`): score 7.46/10, exit status 30 (error/warning/refactor/convention bits), including real E-class
  messages (`E1101` no-member on generated protobuf modules, `E0213` on `__tablename__`); `flake8 app`: 64 F821 (generated code in `app/app`), 76 E111; `black --check app`: 61 files would be
  reformatted (black config in `.toml` is ignored).
- Meaningful coverage today: entity validation, mapper, producers/consumers against mocked Kafka, SmsClient against a mocked Twilio. Not covered:
  worker loops, DI wiring, real Kafka/registry/DB behaviour, migrations, failure paths after the provider call, API error contract.

## 11. Implemented vs only stubbed or documented

| Capability | Status |
|---|---|
| REST submit | Implemented (no auth, brittle errors) |
| Kafka received -> submitted -> sent pipeline | Implemented, incorrect (double publish, shared id, broken ack, swallowed failures) |
| Twilio send | Implemented, untested against realistic response; no timeout |
| Optional sender / messaging service | Half: Twilio branch exists, event/persistence break (#67, PR #74) |
| Delivery callbacks / status tracking | Documented (puml) and abandoned PR #11 only |
| Inbound SMS, STOP/HELP, suppression | Not present |
| Retry/backoff | Producer-side tenacity on one producer only; none on provider or consumers |
| DLQ | TODO comments only |
| Idempotency | Only `identifier` unique and the (sender, recipient, message) constraint, which is wrong semantics |
| Rate limiting, quotas, circuit breaking | Not present |
| Authn/authz, multi-tenancy | Not present (`username`/`password` settings unused) |
| Metrics/tracing/Sentry | Settings only |
| gRPC | Not present |
| Celery workers | Dead code, broken imports (`app/tasks/sms_sending_task.py:4,17`) |
| Docker image / Helm / k8s | Dockerfile stale; nothing else |
| Docs | `docs/Architecture.md` is 0 bytes; README is partly copy-paste from another service (mentions SMTP and Redis) |
