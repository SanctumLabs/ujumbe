> **Status: Proposed. Discovery output dated 2026-10-07; not accepted architecture.** Describes the code as inspected on that date and a proposal for its replacement. Decisions are tracked in the ADR index and open-question log.

# ujumbe: GitHub issues filed

Repository SanctumLabs/ujumbe only. 34 issues created: 6 epics (#76-#81) and 28 children (all attached as sub-issues of their epic). No pre-existing issue (#67-#73) was edited, commented on or reparented; no PR was commented on or reviewed.
Labels used: `severity:P0..P3`, `type:*`, `area:*`, `phase:0..5` (created on first use).

## Epics

| # | URL | Title | Severity | Children |
|---|---|---|---|---|
| 76 | https://github.com/SanctumLabs/ujumbe/issues/76 | Epic: Phase 0 - Restore a trustworthy build, CI and test baseline | P1 | #82 #83 #84 #85 |
| 77 | https://github.com/SanctumLabs/ujumbe/issues/77 | Epic: Phase 1 - Stop message loss, duplicate sends and unsafe defaults | P0 | #86 #87 #88 #89 #90 #91 |
| 78 | https://github.com/SanctumLabs/ujumbe/issues/78 | Epic: Phase 2 - Reliable submission and dispatch pipeline | P0 | #92 #93 #94 #95 #96 #97 |
| 79 | https://github.com/SanctumLabs/ujumbe/issues/79 | Epic: Phase 3 - Delivery lifecycle, callbacks and platform contract | P1 | #98 #99 #100 #101 #102 |
| 80 | https://github.com/SanctumLabs/ujumbe/issues/80 | Epic: Phase 4 - Provider plug-in model, routing and compliance | P2 | #103 #104 #105 |
| 81 | https://github.com/SanctumLabs/ujumbe/issues/81 | Epic: Phase 5 - Security, observability and operability hardening | P1 | #106 #107 #108 #109 |

## Child issues

| # | URL | Title | Sev | Type | Finding IDs | Epic |
|---|---|---|---|---|---|---|
| 82 | https://github.com/SanctumLabs/ujumbe/issues/82 | Fix the failing lint workflow and add required test, build and security gates to CI | P1 | testing | UJU-028 | #76 |
| 83 | https://github.com/SanctumLabs/ujumbe/issues/83 | Repair the red unit suite and test infrastructure; add provider fakes and recorded payload fixtures | P2 | testing | UJU-029 | #76 |
| 84 | https://github.com/SanctumLabs/ujumbe/issues/84 | Replace the stale Dockerfile, Makefile targets and README with deployable, truthful artefacts | P1 | tech-debt | UJU-027 | #76 |
| 85 | https://github.com/SanctumLabs/ujumbe/issues/85 | Remove dead Celery code, duplicate generated protobuf output and unused Kafka/JSON classes | P3 | tech-debt | UJU-030 | #76 |
| 86 | https://github.com/SanctumLabs/ujumbe/issues/86 | Fix Sms entity identity: every Sms created without an id shares one class-level id | P0 | bug | UJU-008 | #77 |
| 87 | https://github.com/SanctumLabs/ujumbe/issues/87 | Apply Kafka TLS/SASL settings to every client and fix the SASL username bug | P1 | security | UJU-011 | #77 |
| 88 | https://github.com/SanctumLabs/ujumbe/issues/88 | Make Kafka publish failures observable and stop blocking the event loop on the submit path | P1 | reliability | UJU-012 | #77 |
| 89 | https://github.com/SanctumLabs/ujumbe/issues/89 | Record provider responses that lack send timestamps instead of crashing after the provider accepted the message | P0 | bug | UJU-009 | #77 |
| 90 | https://github.com/SanctumLabs/ujumbe/issues/90 | Make the stub provider explicit and fail-closed: stop shipping faker in production code and defaulting to fake successes | P1 | bug | UJU-026 | #77 |
| 91 | https://github.com/SanctumLabs/ujumbe/issues/91 | Require authentication and caller identity on the REST send API; disable docs by default outside development | P1 | security | UJU-010 | #77 |
| 92 | https://github.com/SanctumLabs/ujumbe/issues/92 | Fix migration safety: invalid downgrade SQL, CWD-dependent paths, audit trigger on delete, and settings that ignore DB env vars | P2 | bug | UJU-024 | #78 |
| 93 | https://github.com/SanctumLabs/ujumbe/issues/93 | Make provider submission effectively-once: claim with lease before sending and reconcile ambiguous outcomes | P0 | reliability | UJU-035 (UJU-004, UJU-013) | #78 |
| 94 | https://github.com/SanctumLabs/ujumbe/issues/94 | Add provider call resilience: timeouts, error taxonomy, retry budget, circuit breaker and rate limiting | P1 | reliability | UJU-013 | #78 |
| 95 | https://github.com/SanctumLabs/ujumbe/issues/95 | Give workers a real lifecycle: graceful shutdown, health endpoints, back-pressure, concurrency and poison-message handling | P1 | reliability | UJU-014 | #78 |
| 96 | https://github.com/SanctumLabs/ujumbe/issues/96 | Define and enforce the message delivery state machine; persist states as text with a CHECK constraint | P2 | tech-debt | UJU-023 | #78 |
| 97 | https://github.com/SanctumLabs/ujumbe/issues/97 | Fix schema gaps: missing indexes, float money, one-to-many responses, ignored soft delete, no retention or tenant/provider columns | P2 | tech-debt | UJU-025 | #78 |
| 98 | https://github.com/SanctumLabs/ujumbe/issues/98 | Handle inbound SMS and opt-outs: STOP/START/HELP keywords, provider opt-out signals and a pre-send suppression check | P1 | feature | UJU-020 | #79 |
| 99 | https://github.com/SanctumLabs/ujumbe/issues/99 | Fix REST error semantics and response contract: correct status codes, problem details, message id and a status query endpoint | P1 | bug | UJU-017 | #79 |
| 100 | https://github.com/SanctumLabs/ujumbe/issues/100 | Define platform message contract v1: envelope, idempotency, correlation, delivery events, error taxonomy, and REST/gRPC/Kafka bindings | P1 | feature | UJU-017 | #79 |
| 101 | https://github.com/SanctumLabs/ujumbe/issues/101 | Normalize phone numbers to E.164, return validation errors instead of 500, and support alphanumeric sender IDs | P2 | bug | UJU-018 | #79 |
| 102 | https://github.com/SanctumLabs/ujumbe/issues/102 | Model SMS encoding and segments: GSM-7 vs UCS-2 detection, segment and cost estimation, and a correct length rule | P2 | feature | UJU-019 | #79 |
| 103 | https://github.com/SanctumLabs/ujumbe/issues/103 | Add provider routing, health-based failover, per-provider credentials and rate limits on top of the provider port | P2 | feature | UJU-033 | #80 |
| 104 | https://github.com/SanctumLabs/ujumbe/issues/104 | Add sender profiles and a compliance policy layer: registered senders, 10DLC/toll-free/short code/DLT metadata, traffic classes and quiet hours | P2 | feature | UJU-021 | #80 |
| 105 | https://github.com/SanctumLabs/ujumbe/issues/105 | Add rate limiting, quotas, destination allow-lists and SMS-pumping protection per caller | P1 | security | UJU-022 | #80 |
| 106 | https://github.com/SanctumLabs/ujumbe/issues/106 | Stop leaking phone numbers and message bodies: log redaction, exception hygiene, audit trigger replacement, encryption and retention | P1 | security | UJU-015 | #81 |
| 107 | https://github.com/SanctumLabs/ujumbe/issues/107 | Upgrade the runtime stack (Python 3.12+, pydantic v2, SQLAlchemy 2 style, current Twilio SDK) and harden settings and secrets | P2 | tech-debt | UJU-031 | #81 |
| 108 | https://github.com/SanctumLabs/ujumbe/issues/108 | Add load, soak and chaos test suites with capacity numbers for the API, relay and dispatcher | P3 | testing | UJU-034 | #81 |
| 109 | https://github.com/SanctumLabs/ujumbe/issues/109 | Introduce structured single-sink logging, metrics, traces and correlation ids across API, workers and provider calls | P2 | tech-debt | UJU-016 | #81 |

## Existing issues covered, not duplicated (referenced in the bodies above)

| # | Maps to | Where it sits in the plan |
|---|---|---|
| #67 | UJU-001 | Phase 1 (PR #74, merge after changes) |
| #68 | UJU-002 | Phase 1 (PR #75, merge after changes) |
| #69 | UJU-003 | Phase 1 |
| #70 | UJU-004 | Phase 2 (split recommended; #93 is the dispatch-side half) |
| #71 | UJU-005, UJU-032 | Phase 3 (PR #11 to be closed as superseded) |
| #72 | UJU-006 | Phase 4 (decomposition recommended; #103 builds on it) |
| #73 | UJU-007 | Phase 0 (extended by #82, #83, #107) |

Findings without their own issue: UJU-001 to UJU-007 (existing issues), UJU-032 (carried by #71).

## Added on 2026-10-07 after maintainer input

| # | Epic | Title | Sev | Type |
|---|---|---|---|---|
| 111 | #78 | Introduce a broker port with Kafka as the default binding and other brokers pluggable by configuration | P2 | tech-debt |
| 112 | #81 | Package ujumbe as a self-contained, configuration-driven deployable unit | P2 | feature |

Existing issues #67 to #73 now carry labels and parents: #67 (P1, bug, domain, phase 1) and #68 (P0, reliability, pipeline, phase 1) and #69 (P0, reliability, kafka, phase 1) under #77; #70 (P0, reliability, pipeline, phase 2) under #78; #71 (P1, feature, provider, phase 3) under #79; #72 (P2, tech-debt, provider, phase 4) under #80; #73 (P1, testing, build, phase 0) under #76.
Comment added on #93 (resend after reconcile deadline, D6). Reviews posted on PRs #74, #75, #11.
