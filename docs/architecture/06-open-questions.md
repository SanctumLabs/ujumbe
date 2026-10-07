> **Status: Proposed. Discovery output dated 2026-10-07; not accepted architecture.** Describes the code as inspected on that date and a proposal for its replacement. Decisions are tracked in the ADR index and open-question log.

> **Answered on 2026-10-07:** Q-UJU-02 the REST API is not reachable outside the cluster (but must become a standalone deployable unit; #112). Q-UJU-01 broker is Kafka and services stay broker-pluggable (#111); REST remains the baseline. Q-UJU-08 and Q-UJU-10 remain open.

# ujumbe: open questions for a human

Numbering `Q-UJU-NN`. "Default" is what I will assume if nobody answers.

**Q-UJU-01 Who calls ujumbe and over which transport in the target deployment?**
Why: decides whether the Kafka command topic, REST, or gRPC is built first, what authentication is needed, and what the shared contract looks like for niosys and barua-pepe.
Options: (a) niosys only, via Kafka; (b) niosys via REST/gRPC with Kafka as an option per deployment; (c) other internal services too.
Default: (b): one contract (`03-target-design.md` section 4), Kafka command topic and REST `POST /v1/messages` built together on the same application service; gRPC after.

**Q-UJU-02 Is the REST endpoint reachable from outside the cluster/VPC?**
Why: severity of UJU-010 (no auth, open SMS relay): P0 if public.
Options: internal only; behind an API gateway with its own auth; public.
Default: internal only, but add service authentication regardless and disable `/docs` outside dev.

**Q-UJU-03 What is the system of record for delivery state that niosys reads: events only, query API, or both?**
Why: decides event retention, whether `GET /v1/messages/{id}` is needed in phase 3, and how niosys-v2's proven behaviour is folded in.
Options: events only; events + query; query only (polling).
Default: both, events as primary, query for reconciliation and support.

**Q-UJU-04 Who owns opt-out/consent: niosys or ujumbe?**
Why: legal exposure (US TCPA/CTIA STOP handling is a gateway/provider-level duty; marketing consent is upstream); determines whether ujumbe needs its own suppression store and inbound webhook in phase 3.
Options: (a) niosys owns preferences and consent, ujumbe enforces provider-level STOP and reports; (b) ujumbe owns everything for SMS; (c) provider (Twilio Advanced Opt-Out) handles STOP only.
Default: (a), with provider-side STOP handling left on as defence in depth (ADR-7).

**Q-UJU-05 Which countries, sender types and traffic classes must be supported at launch?**
Why: drives sender registration (US 10DLC/toll-free verification, short codes, alphanumeric sender pre-registration, India DLT templates, Kenya/Nigeria/Ghana sender-ID rules), providers needed, and quiet-hour rules. The existing code and defaults hint at Kenya (`+254`), but nothing states it.
Options: list of countries and classes (OTP/transactional/marketing).
Default: Kenya + one other East African market, OTP and transactional only, alphanumeric sender IDs or messaging-service-managed pool; marketing and US traffic out of scope until Q-UJU-04 is settled.

**Q-UJU-06 What volumes and latency targets (peak msg/s, daily messages, OTP latency)?**
Why: sizes partitions, DB, whether Python dispatcher is adequate (ADR-4), outbox polling vs CDC (ADR-2), and sets SLOs. niosys-v2 production numbers would be the best input.
Options: provide niosys-v2 numbers; otherwise assume.
Default: 100 msg/s sustained, 1k msg/s burst, OTP accepted->submitted p95 < 3 s.

**Q-UJU-07 Which providers beyond Twilio, and what are the commercial constraints (volume pricing, sender ID support, regional coverage)?**
Why: shapes the provider port capability model, routing and the second adapter. Africa's Talking, Infobip, Vonage, direct SMPP are typical candidates.
Options: Twilio only for now; Twilio + one regional aggregator; multi-provider least-cost routing.
Default: Twilio + one regional aggregator (failover first, least-cost later).

**Q-UJU-08 Is the Python/FastAPI stack fixed, and which Python version is the target?**
Why: #73 offers either capping or upgrading; Python 3.10 reached end of life on 2026-10-01; pydantic v1 cannot run on 3.14. A rewrite (Go/Kotlin) would change phase 4 and 5 plans.
Options: stay on Python 3.12 (recommended), 3.13 after dependency upgrades, or rewrite.
Default: Python 3.12 now, upgrade pydantic/SQLAlchemy/Twilio in phase 5.

**Q-UJU-09 Are message bodies allowed to be stored, for how long, and may OTP bodies be persisted at all?**
Why: PII/security (UJU-015), storage cost and the audit requirements; GDPR/Kenya DPA/other residency rules.
Options: store encrypted for N days; store hash+metadata only; never store OTP bodies.
Default: encrypt at rest, 30 days for transactional, purge OTP bodies on terminal state + 1 h, metadata 13 months.

**Q-UJU-10 Is the existing production data (rows in `sms`/`sms_responses`, Kafka topics `sms_*_topic`) real, and must it be migrated and the old topics kept?**
Why: given UJU-008, production volume through this code can only have been very low; if there is no real data the migration (phase 2 expand/contract, dual publish window) simplifies to a clean replacement.
Options: no production data (drop and recreate), some data (backfill), significant data.
Default: assume little/no production data but ask for a row count before phase 2.

**Q-UJU-11 What is the intended disposition of the unreviewed Codex/CodeRabbit-authored PRs (#74, #75) and the `codex/*` branch convention?**
Why: both PRs came from automation and their checklists are ticked without truth; deciding whether bot-authored PRs need a human reviewer and a test-quality bar affects process, not code.
Options: require human review and CI green; accept bot reviews only.
Default: require one human review and green CI (once phase 0 lands).

**Q-UJU-12 Should ujumbe keep both the in-repo Kafka client stack and (as attempted in abandoned PR #11) a shared event library (`eventmsg-adaptor`, `sanctumlabs-messageschema`)?**
Why: PR #11 depended on a private GitLab package index; if that library is the platform standard for the other services, the contract and the consumer kit should be shared rather than reinvented.
Options: in-repo kit extracted and shared; adopt the shared library; stay bespoke.
Default: extract a small shared consumer/producer kit with explicit ack and DLQ, adopt shared schemas (buf module) rather than the private runtime library.
