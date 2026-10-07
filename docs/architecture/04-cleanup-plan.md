> **Status: Proposed. Discovery output dated 2026-10-07; not accepted architecture.** Describes the code as inspected on that date and a proposal for its replacement. Decisions are tracked in the ADR index and open-question log.

# ujumbe: phased cleanup plan

Sizes: S <= 2 days, M <= 1.5 weeks, L > 1.5 weeks (one engineer). Risk is risk of regression or rollout harm.
Existing issues #67-#73 are placed in phases but not re-parented (they stay unparented; epics reference them).
Ordering principle: you cannot verify fixes without a working build (phase 0); you cannot build reliability on top of lost or duplicated messages (phase 1); idempotent pipeline before lifecycle features (phase 2 before 3); provider abstraction last because it is the biggest change and the others make it safer (phase 4).

## Phase 0: Restore a trustworthy build, CI and test baseline
Goal: a clean checkout builds, tests run and fail for real reasons, CI gates every PR, images build.
Items: #73 (runtime matrix, cap to 3.12 or upgrade; extended per `08-pr-review.md`); UJU-028 CI (fix `poetry install --no-root` or package mode, run on `pull_request`, add test/lint/format/type/buf/pip-audit/image-scan jobs, fix `.toml` black config and pylint baseline); UJU-029 repair the 10 red unit tests and 2 skips, test settings fixture, provider fakes and recorded payload fixtures, docker-py/testcontainers pair; UJU-027 Dockerfile (multi-stage, non-root) for API and each worker, Makefile and README truth; UJU-030 delete dead Celery and duplicate generated code.
Dependencies: none. Size: M (L if the pydantic v2 / Python upgrade from UJU-031 is pulled in; recommended to keep that to phase 5 and cap Python at 3.12 now).
Risk: low. Exit criteria: `poetry install` + `pytest tests/unit` green on every declared Python in CI; PR checks required on `develop`; images build in CI and start (`/readyz`); coverage report published (no gate yet); zero skipped tests without an issue link; Dependabot PRs only merge on green.

## Phase 1: Stop message loss, duplicate sends and unsafe defaults
Goal: every accepted request is sent at most once under normal operation and failures are visible.
Items (in order): UJU-008 shared Sms id (P0, S); #68 + PR #75 with changes (S); UJU-009 provider response mapping (P0, S-M); #69 Kafka ack semantics (M) together with UJU-011 Kafka TLS/SASL wiring (S) and UJU-012 producer delivery/blocking fixes (M); #67 + PR #74 with changes (S); UJU-026 stub-mode default and faker import (S); UJU-010 minimal authn on the REST API (M).
Dependencies: phase 0 for verification (UJU-008 and UJU-009 are 1-2 hour fixes that should land even before phase 0 finishes, behind their own unit tests). #69 integration tests need phase 0 test infrastructure.
Risk: medium (touches the live pipeline). Rollout: consumers before producers; migration before workers; run old and new for one release; add a "messages accepted vs sent" reconciliation query as a manual check.
Exit criteria: soak test of 10k messages through a local Kafka+Postgres+fake provider shows 10k sent, 0 duplicate provider calls, 0 dropped; killing a worker mid-batch loses nothing; senderless and explicit-sender flows pass end-to-end; PLAINTEXT Kafka refused outside dev; unauthenticated send returns 401.

## Phase 2: Reliable submission and dispatch pipeline
Goal: atomic acceptance, effectively-once provider submission, bounded failure behaviour.
Items: #70 split into idempotency key + constraint removal (M), outbox + relay (M), dispatch claim/lease/reconciler (L); UJU-013 provider resilience (timeouts, error taxonomy, retry budget, circuit breaker) (M); UJU-014 worker lifecycle, health, graceful shutdown, DLQ and replay tooling (M); UJU-023 state machine definition and enforcement, text+check state column (S-M); UJU-024 migration safety fixes + migration CI test (M); UJU-025 schema/index/retention changes via expand/contract (M).
Dependencies: phase 1. State machine before dispatch claim. Outbox before event contract changes. Migration safety before the first new tables.
Risk: high (new tables, behaviour change). Exit criteria: chaos tests pass (kill relay, kill dispatcher mid-call, broker down 10 min, provider 5xx/timeouts) with zero loss and zero double-send in non-ambiguous cases and a measured, documented duplicate rate for ambiguous ones; `ACCEPTED -> terminal` visible per message; migrations apply and roll back on a scratch DB in CI.

## Phase 3: Delivery lifecycle, callbacks and platform contract
Goal: callers can learn what happened to each message, over queue, REST or gRPC.
Items: #71 callbacks (L; signature verification UJU-032 details, `status_callback`, raw event store, projector, unknown/late handling); close PR #11 as superseded; UJU-017 split into API error semantics fix (S-M) and platform contract v1: envelope, correlation, idempotency, events, gRPC service, buf CI (L); UJU-020 inbound MO and STOP handling (M-L); UJU-018 E.164 normalization (S-M); UJU-019 encoding and segment estimation (M).
Dependencies: phase 2 (state machine, outbox). Contract v1 should be agreed with niosys and barua-pepe owners (Q-UJU-01, Q-UJU-03).
Risk: medium (public contract; get it reviewed). Exit criteria: contract tests (producer and consumer sides) in CI; delivered/failed/duplicate/late/unknown callback tests (#71 AC); niosys can submit via Kafka and via REST using the same fixture and read results via events and via `GET`; old topics deprecated with a dated notice.

## Phase 4: Provider plug-in model, routing and compliance
Goal: add a provider by writing one adapter; route by policy; comply by construction.
Items: #72 decomposed (canonical model and `DeliveryProvider` port, Twilio adapter refactor) (L); UJU-033 routing, failover, credentials, per-route rate limits (L); second provider adapter as proof (M); UJU-021 sender profiles and compliance policy (registration refs, traffic classes, quiet hours, template ids where needed) (L); UJU-022 rate limits, quotas, pumping protection (M).
Dependencies: phases 2 and 3. Provider port needs the state machine and error taxonomy first.
Risk: high (largest refactor). Exit criteria: contract test suite that any adapter must pass (recorded payloads + fake server); second provider can be enabled per route in staging; failover drill passes; a tenant cannot send from an unregistered sender or to a disallowed country; budget alarms fire in a test.

## Phase 5: Security, observability and operability hardening
Goal: production-grade operations and data protection.
Items: UJU-015 PII (log redaction, audit replacement, body encryption, retention/erasure) (M-L); UJU-016 logging/metrics/tracing/correlation (M); UJU-031 dependency and runtime upgrade (pydantic v2, SQLAlchemy 2 style, Twilio SDK current, Python 3.12/3.13), secrets handling (M-L); UJU-034 load/soak/chaos suites and capacity numbers (M); SLO dashboards and alerts; runbooks.
Dependencies: can start early for logging (UJU-016) and redaction in parallel with phase 1-2, but the runtime upgrade should follow stabilisation (needs phase 0 tests).
Risk: medium. Exit criteria: no PII in logs (automated test with sentinel number/body), traces visible across API->Kafka->provider, SLO dashboard live, nightly soak green, dependency audit clean, runbooks for provider outage, DLQ replay, key rotation.

## Critical path and parallelism
Phase 0 -> UJU-008/UJU-009 (can start day 1) -> Phase 1 -> Phase 2 (#70) -> Phase 3 (#71) -> Phase 4 (#72).
Parallel tracks: logging/redaction (UJU-015/016), CI hardening, docs; contract design review with niosys and barua-pepe; legal/compliance requirements gathering for UJU-020/021 (Q-UJU-04/05) while engineering proceeds on phases 1-2.
Estimated effort (one engineer, indicative): phase 0 2-3 weeks, phase 1 2-3 weeks, phase 2 5-7 weeks, phase 3 5-6 weeks, phase 4 6-8 weeks, phase 5 4-6 weeks (partly parallel).
