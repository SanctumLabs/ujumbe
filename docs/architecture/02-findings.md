> **Status: Proposed. Discovery output dated 2026-10-07; not accepted architecture.** Describes the code as inspected on that date and a proposal for its replacement. Decisions are tracked in the ADR index and open-question log.

# ujumbe: gap register

Severity: P0 data loss / security-critical / outage-class, P1 serious, P2 important, P3 minor.
V = Verified (read and traced; "Run" = also executed), S = Suspected.
Existing issues #67-#73 (opened 2026-10-04) are mapped, not duplicated. "GH" column is filled after filing (see `07-issues-filed.md`).

## Register

| ID | Sev | Category | Title | Evidence | V/S | GH |
|---|---|---|---|---|---|---|
| UJU-001 | P1 | bug/contract | Requests without sender break event and persistence contracts | `app/services/sms_received_producer.py:36`, `app/database/mapper.py:27,62`, `sms_model.py:30` | V | #67 (PR #74) |
| UJU-002 | P0 | reliability | Every received message publishes `SmsSubmitted` twice | `create_sms.py:26` + `sms_received/__main__.py:39` | V | #68 (PR #75) |
| UJU-003 | P0 | reliability | Kafka auto-commit on, explicit commit path broken | `consumers/__init__.py:24-40,53-71`, `proto_consumer.py:33-37` | V | #69 |
| UJU-004 | P0 | reliability | Dual write, content unique constraint as "idempotency" | `create_sms.py:25-26`, `sms_model.py:22-29` | V | #70 |
| UJU-005 | P1 | feature | No callback ingestion or delivery-state projection | `docs/send_sms_flow.puml:59-67`, `send_sms.py:24-26` | V | #71 (PR #11) |
| UJU-006 | P2 | design | Twilio-shaped domain, no provider abstraction | `sms_response.py:21-35`, `services/sms_service.py` | V | #72 |
| UJU-007 | P1 | testing/build | No runnable supported test environment | `pyproject.toml:8`, poetry.lock | V | #73 |
| UJU-008 | P0 | bug | All `Sms` instances share one id (class-level default) | `app/domain/entities/sms.py:20` | V (Run) | #86 |
| UJU-009 | P0 | bug/reliability | Provider response mapping crashes after the provider accepted the message | `sms_date.py:40-48`, `services/sms_service.py:31-35,58-60`, `sms_response_model.py:35-39` | V (Run, Twilio-shaped fixture; confirm in sandbox) | #89 |
| UJU-010 | P1 | security | REST send API has no authentication, authorization or caller identity | `app/__init__.py:17-31`, `routes.py:16-51` | V (Run) | #91 |
| UJU-011 | P1 | security | Kafka security settings never applied; SASL username set to the password | `kafka_container.py:25-63`, `consumers/__init__.py:37`, `producers/__init__.py:34` | V | #87 |
| UJU-012 | P1 | reliability | Producer cannot detect delivery failure; blocking flush and sleeps inside `async def`; oversize swallowed | `proto_producer.py:36-50`, `callbacks.py:14-18`, `routes.py:23,42`, `sms_received_producer.py:30-31` | V | #88 |
| UJU-013 | P1 | reliability | Provider call has no timeout, error classification, retry budget, circuit breaker or rate limit | `sms_client.py:57-98`; Twilio `TwilioHttpClient` default timeout `None` (Run) | V | #94 |
| UJU-014 | P1 | reliability | Workers: swallow all errors, no graceful shutdown, health, back-pressure or poison-message path | `sms_received/__main__.py:30-44`, `sms_submitted/__main__.py:30-43` | V | #95 (ack/DLQ part: #69) |
| UJU-015 | P1 | security/PII | Phone numbers and message bodies in logs, exceptions, audit trigger and storage | `sms_service.py:28,59-60`, `sms_client.py:59,97-100`, `routes.py:48`, `audit_log.sql:118,193`, `message.py:15` | V | #106 |
| UJU-016 | P2 | observability | Duplicate log sinks, no structure/correlation/metrics/tracing; Sentry unused | `logger.py:14-85` (Run), settings only | V | #109 |
| UJU-017 | P1 | contract | HTTP error semantics wrong; no message id/status API; events lack envelope, correlation, tenant, versioning; no gRPC | `routes.py:44-51`, `exception_handlers.py:11-19`, `events.proto`, `data.proto:54-55` | V (Run) | #99, #100 |
| UJU-018 | P2 | validation | Phone numbers not normalized to E.164; parse errors surface as 500; alphanumeric sender IDs impossible | `phone_number.py:11-14`, `validators.py:4-6`, `dto.py:14` | V (Run) | #101 |
| UJU-019 | P2 | validation | Length/encoding/segmentation model absent (435-char rule, off by one, not GSM-7/UCS-2 aware) | `message.py:5,14` | V (Run) | #102 |
| UJU-020 | P1 | compliance | No opt-out/STOP/consent/suppression handling and no inbound (MO) path | grep: no matches; `SmsType.INBOUND` unused | V | #98 |
| UJU-021 | P2 | compliance | No sender-ID/short-code/10DLC/DLT registry or policy; any caller supplies any sender | `dto.py:14`, `sms_client.py:61-72` | V | #104 |
| UJU-022 | P1 | security/cost | No rate limiting, quotas, destination allow-list or pumping protection | grep: none | V | #105 |
| UJU-023 | P2 | design | Delivery state machine undefined/unenforced; enum persisted as PG native enum; proto zero value is ACCEPTED | `sms_status.py`, `sms_repository.py:52-66`, `send_sms.py:24-26`, `data.proto:54-55` | V | #96 |
| UJU-024 | P2 | db/migrations | Migration safety defects | `migrations/versions/0ad6b839a7f9_initial.py:230`, `ac52bb38b7cf_audit_log.py:27`, `audit_log.sql:176`, `settings.py:60`, `migrations/env.py:13,89` | V (Run for db_url; others by reading) | #92 |
| UJU-025 | P2 | db/schema | Missing indexes, float money, scalar relationship over 1:N data, soft delete ignored, no retention/tenant/provider columns | `sms_response_model.py:61-65,100`, `sms_model.py:38`, repositories | V | #97 |
| UJU-026 | P1 | bug/ops | Stub mode is the default and reports success; `faker` (dev-only) imported by production code; Twilio client needs creds even when disabled | `sms_client.py:6,99-133`, `pyproject.toml` dev group, `settings.py:42` | V (Run) | #90 |
| UJU-027 | P1 | ops | Dockerfile/Makefile/README do not match the code; no worker images | `Dockerfile:1-14`, `Makefile:34-48,87`, README | V | #84 |
| UJU-028 | P1 | ci | Lint workflow fails on every develop push; no test/build/scan jobs; pylint exits 30; black config ignored | `.github/workflows/lint.yml`, Actions runs #146-#154, `.toml` | V (Run + logs) | #82 (CI matrix part: #73) |
| UJU-029 | P2 | testing | Unit suite is red (10) with 2 skips; broken test base; docker-py/requests incompat; mock-only tests | `tests/__init__.py:28`, `tests/unit/api/monitoring/test_routes.py:9-11` | V (Run) | #83 |
| UJU-030 | P3 | tech-debt | Dead/legacy code (Celery, stray `app/app`, unused JSON/simple Kafka classes, bulk DTO, unused settings) | `app/tasks/sms_sending_task.py:4,17`, `app/app/messages`, `kafka/producers/json_producer.py` | V | #85 |
| UJU-031 | P2 | tech-debt | Dependency/runtime/settings hygiene (pydantic v1, Twilio 7, plain-str secrets, env-name mismatches, Python 3.10 EOL) | `pyproject.toml`, `settings.py`, `.env.example` | V | #107 (runtime part overlaps #73) |
| UJU-032 | P1 | security | No webhook ingress, signature verification or `status_callback` request | `sms_client.py:61-72` | V | #71 (details carried by #71; see #98/#100 for ingress reuse) |
| UJU-033 | P2 | design | Single hard-wired provider: no routing, failover, per-provider credentials/rate limits | `gateways_container.py:32-40` | V | #103 (builds on #72) |
| UJU-034 | P3 | testing | No load/soak/chaos harness (`.locust.conf` missing, locust declared) | `Makefile:87-88`, `pyproject.toml` | V | #108 |
| UJU-035 | P0 | reliability | Provider submission is not transactional: no claim/lease, no reconcile of ambiguous outcomes, no client reference | `sms_submitted/__main__.py:30-43`, `send_sms.py:22-28`, `sms_client.py:61-72` | V | #93 (extends #70) |

## Detail

### UJU-001 to UJU-007 (already tracked)
See section "Assessment of existing issues #67-#73" in `08-pr-review.md` for scoping, priority and sufficiency; do not re-file.

### UJU-008 P0 All Sms instances share one id (Verified, executed)
`app/domain/entities/sms.py:20` `id = Entity.next_id()` is evaluated once when the class is created. Every `Sms` built without an explicit id
(i.e. every API request, `Sms.from_dict`, `routes.py:40`) gets the same id for the life of the API process. That id travels in
`SmsReceived.sms.id`; the received worker persists it as `sms.identifier`, which is unique (`base_model.py:21`).
Run: two `Sms.from_dict` objects have equal ids; inserting both through `map_sms_entity_to_model` fails on the second with
`IntegrityError: UNIQUE constraint failed: sms.identifier`. In the worker that becomes `CreateSmsException`, is logged, the loop continues and
auto-commit moves past the record: the API already answered 200. Net effect: only the first message after each API start is ever sent.
Tests miss it because they pass explicit ids (`Sms.next_id().value`).
Impact: silent loss of nearly all traffic; also invalidates any idempotency design built on message identity.
Recommendation: remove the class-level default, use `Field(default_factory=...)` (or accept a client-supplied id/idempotency key), add a test that two
instances differ, and a worker-level test that two submissions persist two rows.

### UJU-009 P0 Provider response mapping crashes after the provider accepted the message (Verified with fixture)
`UjumbeSmsService.send` maps the Twilio response into `SmsDate`, whose validator compares `date_created > date_sent`
(`sms_date.py:40-48`). A newly created Twilio message is `queued` and its `date_sent` is `None`. Run with a Twilio-shaped DTO (`status="queued"`,
`date_sent=None`, `price=None`): `SmsSendingException` caused by `TypeError: '>' not supported between 'datetime' and 'NoneType'`.
The exception happens after `messages.create` returned, so the provider already has (and bills) the message, but nothing is
recorded (`sms_responses.date_sent` is also `nullable=False`, `sms_response_model.py:35-39`), the worker does not commit, and redelivery sends again.
Existing tests use hand-written non-null date strings (`tests/unit/infra/sms/test_sms_client.py:36-38`) which hide this.
Confirm against a Twilio test/sandbox account before relying on the exact payload; the code path itself is fragile regardless.
Recommendation: make provider timestamps optional, keep the provider id as the only mandatory correlation, persist the response inside the
same dispatch transaction, and add a contract test fed with recorded provider payloads (queued, accepted, failed, rejected).

### UJU-010 P1 No authentication or caller identity (Verified, executed)
Run: an unauthenticated `POST /api/v1/sms/` returns 200. `AppSettings.username/password` (`settings.py:117-118`) are never read. Callers can choose
`sender` freely (`dto.py:14`), `/docs` is on by default, there is no tenant concept. Anyone able to reach the port can spend the provider account
and impersonate senders. Priority is P1 on the assumption the service is internal-only; treat as P0 if it is reachable from outside the cluster (Q-UJU-02).
Recommendation: service-to-service authn (mTLS or JWT with audience), per-caller authorization to sender profiles/routes, tenant id on every record,
docs disabled by default outside dev.

### UJU-011 P1 Kafka security not applied; SASL username bug (Verified)
`kafka_container.py:25-63` builds every `KafkaProducerConfig`/`KafkaConsumerConfig` with only bootstrap servers (and topic/group), never the `security`
object, so TLS/SASL settings in `KafkaSettings` have no effect and traffic (including full SMS bodies) is PLAINTEXT. Even if wired,
`self.conf["sasl.username"] = security_config.sasl_password` (consumers `__init__.py:37`, producers `__init__.py:34`) authenticates with the password as username,
and `security.protocol` is set to an enum member rather than a string (`config.py:17-19`). The schema registry client is unauthenticated. Defaults:
`kafka_security_protocol="ssl"`, SASL `ujumbe/ujumbe`.
Recommendation: wire security config, fix the username, use `SecretStr`, add a startup check that refuses PLAINTEXT outside dev, add TLS+SASL (and registry auth) to the compose profile used in integration tests.

### UJU-012 P1 Producer delivery, blocking and flush behaviour (Verified)
`KafkaProtoProducer.produce` calls `produce()` then `flush()` with no timeout, relying on `on_delivery` only to log (`proto_producer.py:36-43`,
`callbacks.py:14-18`; note `message.key` is logged without calling it). A delivery failure after `produce()` is therefore invisible to the caller,
so `SubmitSmsService` returns success and the API answers 200 for a message that was never stored. `MSG_SIZE_TOO_LARGE` is logged and not raised (`proto_producer.py:47-50`).
No `acks=all`, no `enable.idempotence`, no `delivery.timeout.ms`, key is always `None` (no per-message partitioning). The route is `async def`
but calls the synchronous producer, whose `flush()` can block up to the default 5 minute `message.timeout.ms`, plus tenacity `time.sleep` of 3 to 5 s per retry
(`sms_received_producer.py:30-31`), freezing the event loop for all requests. One flush per message caps throughput at one broker round trip.
Recommendation: callback-driven result (future) per message with bounded timeout and raised error, acks=all + idempotent producer, run the blocking client off the event loop (or make `def` route/threadpool), key by message id, remove blocking retries in favour of the outbox (#70).

### UJU-013 P1 Provider call resilience (Verified)
`SmsClient.send` calls the synchronous Twilio client with SDK defaults; `TwilioHttpClient.__init__` `timeout` default is `None` (Run) so a stalled connection blocks the single worker
thread forever; Kafka's `max.poll.interval.ms` then evicts the consumer and the batch is re-delivered (duplicate send). All provider failures are collapsed into `SmsClientException`: no distinction between
invalid recipient (do not retry), opted-out (21610), rate limit (429, back off), auth, provider 5xx (retry/failover), timeout with unknown outcome (reconcile). No retry budget, backoff with jitter, circuit breaker or rate limiter; no use of provider-side idempotency or client reference to reconcile ambiguous outcomes.
Recommendation: explicit connect/read timeouts, typed error taxonomy with retryable flag, circuit breaker per provider/route, token bucket per provider account, reconcile-before-resend for ambiguous outcomes.

### UJU-014 P1 Worker lifecycle (Verified)
Both workers are `while True` with a bare `except Exception` that logs and continues (`sms_received/__main__.py:30-44`), so a poison message or persistent failure becomes silent drops (auto-commit) or a hot loop. No `SIGTERM` handling or `close()`, so rebalances happen with uncommitted work on every deploy; no liveness/readiness, no lag/err metrics, no concurrency model (one message at a time), no pause/resume back-pressure, no `error()` check on polled records (`proto_consumer.py:33-37`). Retry/DLQ policy belongs to #69; this issue is the process model around it.

### UJU-015 P1 PII (Verified)
Full entity reprs (recipient, body, sender) are interpolated into INFO/ERROR logs: `sms_service.py:28,59-60`, `sms_client.py:59,97-100`, workers (line 36), `routes.py:48` (whole payload), `sms_repository.py:33`. `Message.__post_init__` puts the body in the exception text (`message.py:15`), which flows to API/worker logs; for OTP traffic that leaks credentials. The audit trigger copies full rows and the literal client SQL into `audit.log` (`audit_log.sql:118,193`; applied to `sms` and `sms_responses`, initial migration lines 219-220). Bodies and numbers are stored in clear text with no retention or erasure path (soft delete is never applied). Kafka payloads carry the body and the topic has no ACLs in compose.
Recommendation: log ids only, redact number to last 4, structured logger with redaction filter, exclude `message`/`recipient` from audit or drop the audit trigger in favour of an append-only status history, retention job + erasure by recipient hash, hash for dedupe/opt-out matching.

### UJU-016 P2 Logging and observability (Verified, executed)
Six `log.add(...)` sinks to stdout with different minimum levels (`logger.py:14-85`) plus loguru's default stderr sink: Run showed an ERROR line five times and an INFO line three times on stdout. Format has no level, module or request id; no JSON; no trace propagation; Sentry/OTel never initialised; no Prometheus metrics (Prometheus config scrapes Kafka JVM only). No correlation id enters or leaves the service.

### UJU-017 P1 API and event contract (Verified, executed)
- Errors: `AppException` -> HTTP 200 with `status:500` body (`routes.py:47-51`); every other exception -> 500 "Internal server error" including bad phone numbers and over-long messages (Run), because `SubmitSmsException`/`CreateSmsException`/`ValueError`/`NumberParseException` are not mapped. The validation handler keys on pydantic v1 error types (`exception_handlers.py:16`).
- Success text claims "sent" but the request is only accepted; response carries no id (`data=None`), there is no `GET /messages/{id}`, so callers cannot correlate, poll or reconcile.
- Events: protobuf `Sms` wrapper only; no `event_id`, `occurred_at`, `correlation_id`, `causation_id`, `tenant`, `idempotency_key`, `schema_version`, `trace`. `SmsStatus` zero value `ACCEPTED`, no `UNSPECIFIED`; `float price`; Twilio-specific `subresource_uris` in the event. Topic names are not namespaced, key is null, no partition/ordering contract, schema registry compatibility mode unspecified, `buf breaking` configured but never run.
- gRPC is absent although the platform brief requires REST or gRPC or queue as deployment choices.
Recommendation in `03-target-design.md` section 4.

### UJU-018 P2 Phone numbers (Verified, executed)
`PhoneNumber` stores whatever string passed validation (`"+254 700 000 000"`, `"+254700000000\n"`). No E.164 normalization, so dedupe, opt-out matching, rate-limit keys and unique constraints compare unequal strings for the same subscriber. Numbers without `+` raise `NumberParseException` (not `ValueError`) -> 500. No default region, no number-type check (mobile/fixed/VoIP/premium), no geo-permission check. `sender` goes through the same validator so alphanumeric sender IDs (required or preferred in many countries) cannot be used at all.

### UJU-019 P2 Encoding, length and segments (Verified, executed)
`Message` rejects at `>= 435` characters (`message.py:14`, so 435 is rejected, 434 accepted: off by one against the evident intent) counting Python code points. SMS cost and limits depend on encoding: GSM-7 160 (153 per segment when concatenated), UCS-2 70 (67); emoji are two UTF-16 units; GSM-7 extension characters count double; Twilio allows 1600 characters. 434 GSM-7 characters is 3 segments, 434 UCS-2 characters is 7 segments, i.e. a 2.3x cost swing with no estimate, no warning and no cap. Smart-quote normalization and unicode confusables are not handled.

### UJU-020 P1 Opt-out and consent (Verified)
No inbound path, no suppression list, no STOP/UNSTOP/HELP keywords, no handling of provider error 21610 (recipient opted out) beyond a generic failure that is retried or dropped. For US/CA long codes and toll-free this is a legal requirement (TCPA/CTIA); GDPR/ePrivacy/Kenya DPA style consent for marketing traffic lives upstream (niosys preferences) but the gateway must enforce provider-level suppression and report opt-out events upstream. Recommendation: Q-UJU-04 decides ownership; minimum viable is ingest provider opt-out events + pre-send suppression check keyed by normalized recipient and sender profile.

### UJU-021 P2 Sender identity and registration (Verified)
`sender` is a caller-supplied free string validated as a phone number; no registry of senders per tenant/country; no notion of registered brand/campaign (US 10DLC), toll-free verification, short codes, alphanumeric sender pre-registration (many countries), or India DLT entity/header/template ids; no traffic classes (OTP/transactional/marketing) with different routes and quiet-hour rules; no per-country policy (opt-in wording, time windows). #67 introduces "originator policy" but only as senderless-versus-sender selection.

### UJU-022 P1 Rate limits, quotas, pumping protection (Verified)
Nothing limits requests per caller, per destination, per country or per time window, and there is no spend ceiling; combined with UJU-010 this is the classic SMS pumping/toll-fraud shape. `SmsPrice` is a float and cost is only learned after sending (`price` is often `None` at creation). Recommendation: token buckets per caller/destination/prefix, destination-country allow-list, per-tenant daily budget with alert, anomaly alerts on conversion (delivery) ratio.

### UJU-023 P2 State machine (Verified)
13 states, no transition table, `SmsDatabaseRepository.update` overwrites status unconditionally (`sms_repository.py:52-66`), `SendSmsService` never updates it, `from_dict` defaults to UNKNOWN while producers hard-code PENDING/SENT. Twilio states `delivery_unknown`, `partially_delivered`, `receiving`, `received` map to UNKNOWN or exist without meaning. Persisted as PostgreSQL native enum (`Enum(SmsDeliveryStatus)`), so adding a state requires `ALTER TYPE ... ADD VALUE` outside a transaction block on older PG and breaks mixed-version rollouts; proto enum has no unspecified zero. Recommendation in `03-target-design.md` section 6.

### UJU-024 P2 Migration safety (Verified by reading unless noted)
- `0ad6b839a7f9` downgrade runs `DROP TYPE public.'smsdeliverystatus'` (quoted with single quotes: invalid SQL), so `make migrate-down` fails after dropping the tables.
- `ac52bb38b7cf` opens `migrations/sql/audit_log.sql` by a relative path, so it only works when run from the repo root (not from an image where migrations are copied elsewhere).
- `audit.if_modified_func()` reads `NEW.updated_by` in the DELETE branch (`audit_log.sql:176`); `NEW` is not assigned for DELETE in a row trigger, so `SmsDatabaseRepository.remove` is expected to fail on an audited table. (Not executed: no PostgreSQL available; confirm.)
- `db_url` is built at class definition from default values (`settings.py:60`); Run showed `DB_HOST=db.prod` is ignored; Alembic uses it (`migrations/env.py:13,89`), so a migration can silently target the wrong database. It also has no driver (`postgresql://`).
- PR #74's migration is a nullable change (metadata-only, safe online) but its downgrade is `NotImplementedError`.
- No migration test in CI (integration tests use `Base.metadata.create_all`), no `lock_timeout`/`statement_timeout`, no expand/contract convention, native enum.

### UJU-025 P2 Schema (Verified)
No index on `sms_responses.sms_id`, `sms.recipient`, `sms.delivery_status`; `price` and `num_*` as float/int mixed types, money as `Float` (`sms_response_model.py:61-65`); 1:N possible but modelled scalar (`Mapped[Optional[SmsResponse]]`), so a duplicate send yields a second row that breaks mapping; `deleted_at` default sentinel is never filtered in queries; unbounded growth with no partitioning or retention; no provider/route/tenant/correlation columns; `get_all()` loads the entire table.

### UJU-026 P1 Stub mode and dev-only import (Verified, executed)
Default `TWILIO_ENABLED=False` (`settings.py:42`, `.env.example:7`) makes `SmsClient.send` return a fabricated successful response (`sms_client.py:99-133`): the pipeline reports SENT and persists fake rows while nothing is sent. A deployment that forgets the flag silently black-holes SMS with no alert. `from faker import Faker` is a module-level import of a package declared only in the dev group, so `poetry install --only main` yields `ImportError` at startup. `SmsClient.__init__` builds the Twilio client unconditionally, and with empty credentials raises `TwilioException: Credentials are required` (Run), contradicting the README claim that Twilio is "stubbed out" by default.
Recommendation: a real in-process `FakeProvider` adapter selected explicitly (never default in non-dev), startup validation that a real provider is configured outside dev, remove faker from runtime.

### UJU-027 P1 Deployment artefacts (Verified)
`Dockerfile`: `python:3.8.6-alpine3.11`, `pipenv lock -r`, `gunicorn --config config/gunicorn_config.py wsgi:app`; no Pipfile, config dir or wsgi module exists. Alpine plus confluent-kafka/psycopg2 builds are not viable as written. No image for the two workers, no non-root user, no HEALTHCHECK, no pinned base digest, no `.dockerignore` for tests/docs. Makefile targets reference non-existent files (section 8 of `01`). README still describes SMTP and Python 3.8 and links an empty `docs/Architecture.md`.

### UJU-028 P1 CI (Verified)
`lint.yml` runs on `push` only (not `pull_request`), uses `actions/checkout@v3`/`setup-python@v2` (Node 20 deprecation warnings in log), `poetry install` without `--no-root` in a repo with no package directory: fails with "No file/folder found for package ujumbe" (log of run 37276089746). `develop` runs #146, #148, #150, #153, #154 all failed. Even with that fixed, `make lint` = `pylint app` exits 30 (score 7.46). There is no job that runs tests, builds an image, runs `buf lint/breaking`, scans dependencies or images, or applies migrations to a scratch DB. Branch protection exists on `develop` but required checks cannot pass meaningfully.

### UJU-029 P2 Tests (Verified, executed)
See `05-test-strategy.md` section 1. Highlights: 10 red unit tests, 2 skips with "TODO" reasons, test base class constructs settings that do not exist (`tests/__init__.py:28`), worker `main()` untested, producer/consumer tests mock the Kafka client so none touches serialization against a registry, no provider payload fixtures, no contract tests, integration tests cannot start with the locked docker-py/requests pair.

### UJU-030 P3 Dead code
`app/tasks/sms_sending_task.py:4` imports `send_sms` from `app.services.sms_service` (does not exist) and reads `data.phone_number` (no such attribute); `app/tasks/save_sms_task.py` empty; Celery queue constants; `app/app/messages/events/**` duplicate generated modules (source of 64 flake8 F821); JSON/simple Kafka producers/serializers/deserializers, `BulkSmsRequestDto`, `KafkaConsumer.reset_offset` (resets to beginning, unused); `CreateSmsService` exceptions without `from`.

### UJU-031 P2 Dependency and settings hygiene (Verified)
pydantic 1.10.13 (v1 EOL, no 3.14 support), Twilio 7.17.0, confluent-kafka 2.0.2 (3 years old), `greenlet 3.0.0rc3` pinned to a release candidate, testcontainers `0.0.1rc1`, `kafka-python` (transitive test-only dependency, not declared) bumped by Dependabot, `faker` at runtime, `anyio 4.14` bumped under starlette 0.35 without tests being able to run. Secrets are plain `str` (`TwilioSmsClientSettings`, SASL), `SmsClientParams` dataclass repr would print the auth token. Env var names in `.env.example` do not match settings fields. Python 3.10 reached end of life on 2026-10-01 and is what CI uses. Dependabot merges proceed with a failing CI and no tests, so bumps are unverified (e.g. requests 2.33 broke docker-py 6).

### UJU-032 P1 Webhook ingress and signatures (covered by #71)
Beyond #71's acceptance criteria, the design must cover: Twilio posts `application/x-www-form-urlencoded`, signs `X-Twilio-Signature` (HMAC-SHA1 of full URL plus sorted params with the auth token), so validation must use the externally visible URL behind proxies; use constant-time compare; per-provider secret lookup supporting rotation (accept old and new); optional timestamp/replay window; rate-limit the endpoint; always respond 2xx quickly after durable enqueue; and `messages.create` must request callbacks (`status_callback` or Messaging Service-level config) which the current client never sets (`sms_client.py:62-72`). PR #11's endpoint takes JSON, has no verification and would not work with Twilio.

### UJU-033 P2 Provider routing and credentials
One `SmsClient` singleton (`gateways_container.py:32-40`), global credentials, no route table (country/traffic class/tenant -> provider), no health scoring, no failover rule. Failover is dangerous with ambiguous outcomes: fail over only on definite pre-acceptance rejection, never after a timeout without reconciliation. Credentials should come from a secret store with versioning, not process env.

### UJU-034 P3 Load testing
`locust` is a dev dependency and `make load-test` points at a missing `.locust.conf`; there are no capacity numbers, no soak or chaos tests (broker down, provider 5xx, slow provider, duplicate delivery).

### UJU-035 P0 Provider submission is not transactional (Verified by reading)
See issue #93 and `03-target-design.md` section 6. The sender worker has no state check, claim or lease before calling the provider and no way to reconcile an ambiguous outcome (read timeout, connection reset, crash between accept and result commit). Any redelivery sends again. This is the true exactly-once boundary and is only mentioned in one sentence of #70.
