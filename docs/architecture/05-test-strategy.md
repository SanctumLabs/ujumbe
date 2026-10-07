> **Status: Proposed. Discovery output dated 2026-10-07; not accepted architecture.** Describes the code as inspected on that date and a proposal for its replacement. Decisions are tracked in the ADR index and open-question log.

# ujumbe: test strategy

## 1. Current test reality (measured)

Environment used: Python 3.11.17, versions from `poetry.lock` (psycopg2 replaced by psycopg2-binary because the sandbox lacks Python headers), scratch copy of `develop` @ `6b097ec`.

| Suite | Files / lines | Result | Why |
|---|---|---|---|
| `tests/unit` | 27 files, ~1.9k lines | **10 failed, 57 passed, 2 skipped** (7.9 s) | see below |
| `tests/integration` | 4 files (Postgres and Kafka via testcontainers) | **22 errors** | docker-py 6.0.1 + locked requests 2.33.0: `Not supported URL scheme http+docker`; testcontainers 0.0.1rc1 teardown `AttributeError: _container`; no Docker daemon in this sandbox; 2 Kafka tests are unconditionally skipped ("schema registry failing to connect") |
| `tests/e2e` | empty package | n/a | |
| Linters | | pylint 7.46/10 exit 30; flake8 64 F821 (generated code) + 76 E111; black wants to reformat 61 files | black config sits in `.toml` (ignored) |
| CI | | Lint workflow red on every `develop` push; no test job | `poetry install` fails ("No file/folder found for package ujumbe") |

Failure causes (unit):
1. 8 API tests: `tests/__init__.py:28` calls `AppSettings(environment="test", sentry_debug_enabled=False, sentry_enabled=False, sentry_dsn="")`; those fields live in nested `SentrySettings`, pydantic v1 raises `extra fields not permitted`. Every `setUp` of every API test fails; the API surface is effectively untested.
2. `MonitoringRoutesTestCases`: `@pytest.mark.anyio` on a `unittest.TestCase` skips `setUp`, so `self.async_client` is missing.
3. `SmsReceivedProducerTestCases.test_throws_exception_when_there_is_an_error_producing_message`: asserts `produce` called once but the tenacity `@retry` calls it three times with real 3 s sleeps (stale test; slow test).
4. 2 skips: a worker test whose `main()` loops forever (PR #75 deletes it instead of fixing it) and an API route test with an unexplained mocking failure.

Is it meaningful? Partly. Good: value-object validation, mapper round trips, producer/consumer serialization against real generated protobuf classes, `SmsClient` branching against a mocked Twilio `messages`. Missing or misleading: nothing exercises the worker loops, DI wiring, commit/ack behaviour, the actual Kafka/registry wire format, DB constraints under real Postgres through Alembic (integration tests use `create_all`), failure after the provider call, or the HTTP error contract. Mocks assert call counts (`assert_called_once`) rather than outcomes, and fixtures are hand-written (non-null dates) so real provider payloads never hit the code (UJU-009 and UJU-008 both passed unnoticed). Faker random data is unseeded.

## 2. Target pyramid

| Layer | Share | What | Tooling |
|---|---|---|---|
| Unit (domain, mappers, policy, state machine, error mapping) | ~60% | pure functions, property-based where valuable (E.164, segments, state transitions) | pytest, hypothesis, no I/O, < 60 s total |
| Component/adapter (DB repositories, outbox, relay, projector, dispatcher against fakes) | ~20% | real Postgres (service container in CI, not testcontainers-in-docker if avoidable), Alembic-built schema | pytest + `postgres:16` service, `alembic upgrade head` in fixture |
| Contract tests | ~10% | (a) inbound/outbound schema contracts shared with niosys/barua-pepe; (b) provider adapter contract suite | buf lint/breaking, schema-registry compatibility check, Pact-style/JSON-schema consumer tests, recorded provider payloads |
| Integration (Kafka + Postgres + fake provider + registry) | ~8% | the real pipeline end to end in Compose | pytest + compose profile (Redpanda or Kafka KRaft, registry), fake provider server |
| Non-functional (load, soak, chaos, security) | ~2% by count, scheduled | | locust or k6, toxiproxy, Schemathesis, bandit/semgrep, pip-audit, trivy |

## 3. Contract tests

- **Platform contract (4.1/4.2 of `03-target-design.md`)**: protobuf files are the single source; CI runs `buf lint`, `buf breaking --against '.git#branch=develop'` (CI fetches the `develop` branch first), and registers schemas against a throw-away registry in `BACKWARD_TRANSITIVE` mode. Golden fixtures (one JSON/proto per event and command) live in a shared `contracts/` directory consumed by both ujumbe and the niosys adapter tests; a change to a golden fixture requires the other repo's CI to pass (Pact broker or a simple versioned artifact).
- **REST/gRPC parity test**: the same fixture set is sent through REST, gRPC and Kafka command consumer and must produce identical persisted state and events.
- **Provider adapter contract suite**: a single parametrized test module that every adapter must pass: capabilities declaration; success -> `SUBMITTED`; each documented provider error -> canonical error code/category/retryable (golden table); timeout -> ambiguous; callback signature valid/invalid/rotated secret; callback payloads (delivered, undelivered, failed, out-of-order, duplicate) -> expected `DeliveryReport`s; inbound STOP.
- **Provider fakes**: (1) in-process `FakeProvider` implementing the port with scriptable outcomes (accept, reject codes, delay, 5xx, timeout after accept, duplicate callback) used by unit/component tests; (2) HTTP fake server (FastAPI app emulating Twilio's `Messages.json` and posting signed callbacks) for integration/e2e and local development, replacing the faker-based stub inside production code (UJU-026). Twilio's own test credentials and magic numbers (`+15005550006` valid, `+15005550001` invalid etc.) used in a nightly smoke against the real sandbox, never in PR gates.

## 4. Load, soak, chaos

- **Load** (locust/k6 against Compose or an ephemeral cluster): API accept rate to find the DB-bound ceiling (target 1k msg/s accepted, p99 < 300 ms); dispatch throughput against the fake provider with injected latency (200 ms) and per-route 30 MPS limit to verify rate limiting and back-pressure.
- **Soak** (nightly, 2-4 h at 30% of ceiling): memory/FD leaks, consumer lag stability, outbox lag, connection pool behaviour, log volume.
- **Chaos** (toxiproxy/`docker kill`): broker down 10 min; broker leader change; Postgres failover (connection drop mid-transaction); provider 5xx, 429 storms, slow responses, accept-then-timeout, duplicate and out-of-order callbacks; kill dispatcher between provider accept and result commit; kill relay between publish and mark-published; clock skew. Invariants checked by a reconciliation query after each run: every `ACCEPTED` message reaches a terminal state or an alarmed `UNKNOWN_FINAL`; provider-side accepted count (from the fake) equals messages in SUBMITTED+ states except the documented ambiguous set; no message has two successful provider submissions.
- **Security tests**: unauthenticated and cross-tenant access, forged callback signatures, replayed callbacks, oversize bodies, phone number fuzzing (Schemathesis + hypothesis), SSRF on callback URLs, log scan for sentinel PII.

## 5. Coverage and mutation gates

- Phase 0: coverage measured, no gate. Phase 2: gate 80% line / 70% branch overall, 90% on domain, policy, state machine, adapters' error mapping, outbox/relay/dispatcher (diff coverage >= 90% on PRs via `diff-cover`).
- Mutation testing (mutmut or cosmic-ray) on domain + policy + state machine + idempotency code, nightly, threshold: surviving mutants < 15%; start as report-only. The unit test added by PR #75 (a mock called once) is the kind of test mutation testing would reveal as vacuous.
- Test quality rules: no test may be skipped without a linked issue; no `assert_called_once` as the only assertion for an observable behaviour; no unseeded randomness (seed Faker, Hypothesis database committed for failures); tests must fail when the targeted bug is reintroduced (verify by reverting the fix in review for bug-fix PRs).

## 6. CI gates (per PR, required on `develop`)

1. `poetry install --no-root` (or package mode fixed), lock consistency (`poetry check --lock`), Python matrix = every declared version (#73).
2. Format and lint (ruff or black+isort+flake8; pylint kept only if it can be made to pass; mypy on `app/domain` and `app/core` first).
3. Unit + component tests with coverage and diff-cover; Postgres service container; migrations: `alembic upgrade head`, `alembic downgrade -1` and `upgrade head` again, and `alembic check` (model/migration drift).
4. `buf lint`, `buf breaking`, registry compatibility check; generated code up to date (`buf generate` + `git diff --exit-code`), and `app/app` stray output removed.
5. Docker build of API and worker images, run container health checks, image scan (trivy) and `pip-audit`; secret scan; CodeQL (already present).
6. Integration job (Compose: Postgres, Kafka, registry, fake provider) on PR for touched areas and nightly for everything; contract tests with niosys fixtures.
7. Nightly: soak, chaos subset, mutation report, Twilio sandbox smoke.
8. Dependabot: auto-merge only for patch updates with green required checks.

## 7. Test data and fixtures standards

- Builders (`SmsBuilder`, `SendCommandBuilder`) with explicit defaults and `.with_*` overrides; no shared mutable module-level objects (the `create_mock_sms_response(sms_identifier=fake.uuid4())` default argument is evaluated once at import).
- Phone numbers: use only reserved/test ranges (Twilio magic numbers, `+1555...`) in live-provider tests. Numbers such as `+254700000000` are not guaranteed unreachable, so keep them in one `fixtures/numbers.py` for fake-provider tests only; a sentinel pair (`+15005550006`, body `PII-SENTINEL-BODY-xyz`) used by the log-scan test.
- Provider payloads: recorded real (sanitized) responses stored as JSON under `tests/fixtures/providers/<provider>/`, each with a header describing capture date and API version; refreshed by a script; every mapper test runs against them (this alone would have exposed UJU-009).
- Time: injectable clock; no `sleep` in tests (tenacity waits patched or retry delegated to outbox/delay topics).
- DB: one fixture creates schema through Alembic, per-test transaction rollback or truncate; no `create_all`.
- Kafka: Compose services with unique topic/group per test run; helpers for produce-and-wait with timeouts; assert on committed offsets via admin API, not mocks.

## 8. First 10 tests to write (in order)

1. **Unique ids** (unit): two `Sms.from_dict` objects have different ids; and `Sms(...)` with explicit id keeps it. Fails today (UJU-008).
2. **Two submissions persist** (component, Postgres or sqlite fixture): two API-created `Sms` objects both insert; second must not raise. Fails today.
3. **Provider payload mapping** (unit): feed recorded Twilio `queued` response with `date_sent=None`, `price=None`, string `num_segments` into `UjumbeSmsService`/adapter; assert a `SmsResponse`/`SubmitResult` is produced and nothing raises. Fails today (UJU-009).
4. **Worker publishes once** (component): real `CreateSmsService` + fake repository + fake producer; drive one `SmsReceived` through the worker's per-message function; assert one `SmsSubmitted` publish and one commit, and that a repository failure yields no commit. (Replaces the vacuous test in PR #75.)
5. **Ack only after success** (integration, real Kafka): consumer with auto-commit off; handler raises -> offset unchanged after restart (message redelivered); handler succeeds -> committed exactly once. Fails today (#69).
6. **Senderless end-to-end** (integration/component): `POST` without sender -> event without `sender` -> persisted NULL -> `messages.create(messaging_service_sid=...)` called with the configured SID; explicit sender uses `from_`; missing SID configuration fails fast with a clear error (#67 + PR #74 changes).
7. **API error contract** (unit with fixed test base): invalid phone -> 422 with error code `INVALID_RECIPIENT`; oversized body -> 422 `BODY_TOO_LONG`; broker unavailable -> 503; success -> 202 with `message_id`; no response uses HTTP 200 with an error body (UJU-017).
8. **Idempotent submit** (component): same `Idempotency-Key` twice -> one message, one outbox row, same id returned; same key with different body -> 409; identical body with a new key -> new message (legitimate repeat) (#70).
9. **Callback state projection** (component): delivered, failed, duplicate, out-of-order (`delivered` then `sent`), unknown provider id, bad signature (rejected, no state change) using Twilio-signed fixtures (#71).
10. **Crash between provider accept and result commit** (chaos/integration with fake provider): kill dispatcher after the fake accepted; on restart the reconciler looks up by client reference, marks `SUBMITTED`, and the fake shows exactly one accepted message (UJU-013/#70 dispatch claim).
