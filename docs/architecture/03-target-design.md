> **Status: Proposed. Discovery output dated 2026-10-07; not accepted architecture.** Describes the code as inspected on that date and a proposal for its replacement. Decisions are tracked in the ADR index and open-question log.
>
> **Superseded or added points (maintainer decisions, 2026-10-07; see niosys `docs/platform/18-decision-log.md`).**
> 1. **Ambiguous outcomes (section 6, ADR on exactly-once):** the rule "only if the provider confirms nothing was created is a new attempt made" is replaced. A missed message is worse than a duplicate: reconcile by lookup; if the provider cannot confirm by the deadline, **resend, capped and counted**, with an alert on the resend rate. Still no failover before reconciliation (issue #93 amended).
> 2. **Broker:** Kafka stays the production broker, behind a **broker port** so RabbitMQ or another broker can be configured (issue #111).
> 3. **Deployability:** ujumbe must be deployable as a self-contained unit, configured entirely by environment, with no dependency on other platform services (issue #112, ADR P-16).
> 4. **Exposure:** the REST API is internal-only today, so unauthenticated access (#91) stays P1.
> 5. **Optional validity bound (proposed, not final):** no new attempt after `expires_at`; resend-after-unknown only within validity; `EXPIRED` is terminal and alerted; OTP-class default 5 minutes, general default to be ratified (comment on #93).

# ujumbe: target design

Scope: the SMS channel gateway in the notification platform (niosys orchestrates, ujumbe sends SMS, barua-pepe sends email). This design builds on, and does not replace, the intent of open issues #67-#73; where it differs it says so.

## 1. Boundaries and responsibilities

ujumbe owns: accepting an SMS send command, making it durable, dispatching through exactly one provider route per attempt, tracking the delivery lifecycle, absorbing provider callbacks and inbound traffic, enforcing provider/carrier-level compliance (sender registration, suppression of STOP recipients, rate and spend limits), and reporting results back.
ujumbe does not own: user notification preferences, channel choice, templating, scheduling policy, marketing consent (niosys), and anything about other channels.
Rule: ujumbe never decides *whether* to notify, only *whether it may and how* to send over SMS. It must be callable with no knowledge of niosys, and report results through a contract that any caller can consume.

## 2. Components

```
              +---------------------------- ujumbe ----------------------------+
 REST/gRPC -->| Ingress API  --txn--> [messages + outbox + idempotency]  (PG)    |
 Kafka cmd -->| (authn/z, validate,        |                                    |
              |  normalize, policy)        v                                    |
              |                       Outbox relay --> Kafka topics (internal)  |
              |                                            |                    |
              |  Dispatcher workers  <-- sms.dispatch.v1 --+                    |
              |   claim -> route -> rate-limit -> Provider port -> adapter ---> | Twilio / Infobip / AT / ...
              |   record attempt (txn) -> emit events                           |
              |                                                                 |
 provider --->| Callback ingress (verify signature, persist raw, enqueue) -----> |
 webhooks     |  Projector: monotonic state transition + history + events       |
              |  Inbound MO ingress -> opt-out processor -> suppression list    |
              |  Reconciler (stuck SENDING, unknown callbacks, provider polling) |
              +--------------------- events out: Kafka / REST webhook / gRPC ----+
```

1. **Ingress API** (FastAPI, keep): `POST /v1/messages`, `GET /v1/messages/{id}`, `POST /v1/messages:batch`, `GET /v1/messages/{id}/events`. Same logical command is accepted from a Kafka command topic by a thin consumer that calls the same application service. Authn (mTLS or JWT), tenant resolution, schema validation, E.164 normalization, policy checks (section 8), then one DB transaction: upsert idempotency record, insert message (state `ACCEPTED`), insert outbox row. Returns `202 Accepted` with `message_id`.
2. **Outbox relay**: claims unpublished rows (`FOR UPDATE SKIP LOCKED`), publishes to the internal `sms.dispatch.v1` topic keyed by `route_key` (see 6), marks published. At-least-once by design; consumers dedupe.
3. **Dispatcher** (stateless worker pool): consumes dispatch events; in one short transaction moves the message `QUEUED -> SENDING` with a lease (`claimed_by`, `lease_until`, `attempt_no`) using a conditional update; commits; calls the provider outside the transaction with a client reference equal to `message_id` and attempt number; records the result; moves to `SUBMITTED` / retry / `FAILED`. Offset is committed only after the result transaction.
4. **Provider port** (`DeliveryProvider`): `send(request) -> SubmitResult`, `lookup(client_ref | provider_id) -> ProviderStatus`, `parse_callback(raw) -> list[DeliveryReport]`, `verify_callback(raw, headers, url) -> bool`, `capabilities() -> {encodings, max_segments, sender_types, countries, supports_idempotency, supports_status_callback, rate_limits}`. Adapters (Twilio first) own translation of provider fields and error codes into the canonical taxonomy (section 5). Domain never sees provider field names.
5. **Router**: pure function `(tenant, traffic_class, destination_country, sender_profile) -> ordered list of routes`, each route = provider account + sender profile + limits, with health (circuit state) and cost weight.
6. **Callback ingress + Projector**: verified provider webhooks are stored raw (`provider_events`), deduped by `(provider, provider_event_id | hash)`, then the projector applies a monotonic transition to the message and appends to `message_events`. Unknown provider ids are parked and re-tried by the reconciler.
7. **Inbound MO + opt-out processor**: inbound messages (including STOP/START/HELP keywords and provider "opted out" signals) update the `suppressions` table and emit `RecipientOptedOut`/`RecipientOptedIn`.
8. **Reconciler** (scheduled): leases expired in `SENDING` -> `lookup()` provider by client reference before any resend; stuck `SUBMITTED` older than a TTL -> poll provider status or mark `UNKNOWN_FINAL` with an alert.
9. **Event publisher**: outbound events written to the same outbox and published to `sms.events.v1` (and optionally delivered as signed webhooks to registered callback URLs).

Runtime: keep Python/FastAPI (ADR-4), move to sync-safe async: async Kafka client wrapper or thread pool for blocking calls; dispatcher concurrency via N partitions x M worker threads with per-route semaphores.

## 3. Data model (PostgreSQL)

All timestamps `timestamptz`, ids `uuid`/ULID text, text columns for states (check constraint, not native enum), money as `numeric(12,6)` + `currency char(3)`.

```
tenants(id, name, status, daily_spend_limit, created_at)
sender_profiles(id, tenant_id, kind {numeric|alphanumeric|shortcode|tollfree|10dlc|messaging_service}, value, countries[], 
                registration_ref, traffic_classes[], status, provider_route_ids[])
routes(id, provider, account_ref(secret id), country_scope, traffic_class, priority, weight, rate_limit_per_s, status)
messages(id pk, tenant_id, idempotency_key, request_hash, correlation_id, caused_by,
         recipient_e164, recipient_hash, sender_profile_id, traffic_class, body_ciphertext/body (see 8), encoding, segments_est,
         state, state_rank, state_updated_at, not_before, expires_at, created_at,
         unique(tenant_id, idempotency_key))
message_attempts(id, message_id, attempt_no, route_id, claimed_by, lease_until, client_ref, provider_message_id,
                 outcome, error_code, retryable, request_at, response_at, cost_amount, cost_currency, segments, unique(message_id, attempt_no))
message_events(id, message_id, seq, state, source {api|dispatcher|callback|reconciler}, provider_event_id, occurred_at, received_at,
               error_code, detail jsonb)   -- append-only, replaces audit trigger as the history
provider_events(id, provider, provider_event_id, raw bytea/jsonb, signature_ok, received_at, processed_at, message_id null)  -- unique(provider, provider_event_id)
outbox(id bigserial, topic, key, payload bytea, headers jsonb, created_at, published_at null)  -- partial index where published_at is null
suppressions(tenant_id, recipient_hash, scope {sender_profile|tenant|global}, reason, source_event, created_at)
inbound_messages(id, provider, provider_message_id, from_hash, to_ref, body_ciphertext, received_at)
```
Notes: unique `(tenant_id, idempotency_key)` replaces `(sender, recipient, message)`; `request_hash` detects key reuse with a different payload (409). `recipient_hash = HMAC(pepper, e164)` serves dedupe, rate limiting and suppression without exposing numbers in logs. Monthly range partitioning on `messages`/`message_events` with retention job (default 90 days body, 13 months metadata; tenant-configurable). Existing `sms`/`sms_responses` migrate with expand/contract (section 10).

## 4. Contracts (transport-agnostic)

One logical contract, three bindings: Kafka (protobuf + schema registry, with `buf breaking` as a CI gate), REST/JSON (`/v1`; the canonical field names are the snake_case names used in the examples below. The default ProtoJSON mapping emits lowerCamelCase, so serializers must preserve proto field names, for example `preserving_proto_field_name=True` in Python, and parsers should accept both spellings), gRPC (same `.proto` service). Envelope fields are identical on all transports; on REST they travel as headers/body, on Kafka as message headers + value.

### 4.1 Inbound command: `SendMessage` (REST `POST /v1/messages`, gRPC `MessagingService.Send`, Kafka topic `sms.commands.v1`)
```
envelope:
  message_id       string  optional, client-generated ULID/UUID; if absent the service generates and returns one
  idempotency_key  string  required (REST: Idempotency-Key header); unique per tenant for >= 24 h
  correlation_id   string  required for propagation (REST: X-Correlation-Id; generated if missing); echoed on every event
  causation_id     string  optional (id of the triggering event in the caller)
  tenant_id        string  derived from credentials, not trusted from the body (Kafka: from verified header/ACL principal)
  schema_version   string  "1"
  occurred_at      timestamp
body:
  to               string  E.164 or national + region_hint
  from             SenderRef { sender_profile_id | sender_id (alphanumeric) | number } optional
                           (absent = tenant default profile for the destination; resolves #67 without a provider-specific concept)
  text             string  UTF-8
  traffic_class    enum    OTP | TRANSACTIONAL | MARKETING   (drives route, quiet hours, suppression scope)
  not_before / expires_at   timestamps (validity period; OTP default 5 min)
  encoding_hint    enum    AUTO | GSM7 | UCS2 ; max_segments uint (default 3, cost guard)
  callback         { url | topic } optional override of default event destination
  metadata         map<string,string> (<= 16 keys, never logged)
  consent          { basis, recorded_at } optional assertion from caller, stored for audit (ADR-7)
```
Response (202): `{ message_id, state: "ACCEPTED", segments_estimate, encoding, correlation_id }`. Duplicate key + same payload -> 200/202 with the original `message_id`; same key different payload -> 409 `IDEMPOTENCY_KEY_REUSED`.

### 4.2 Outbound events (Kafka topic `sms.events.v1`, key = `message_id`; same payloads for webhook/gRPC streaming)
```
common: event_id (ULID), event_type, schema_version, occurred_at, message_id, tenant_id, correlation_id, causation_id, sequence (per message, monotonic)
MessageAccepted       { recipient_hash, segments_estimate, traffic_class }
MessageDispatched     { route_id, provider, attempt_no, provider_message_id? }
MessageStateChanged   { from_state, to_state, reason, provider, provider_message_id, error{code,category,retryable,detail}, segments, cost{amount,currency}, terminal }
MessageFailed         { error{code,category,retryable=false,detail}, attempts }          (terminal convenience event)
InboundMessageReceived{ inbound_id, from_hash, to_ref, text?, received_at }
RecipientOptedOut / RecipientOptedIn { tenant_id, recipient_hash, scope, source }
```
PII rule: events carry `recipient_hash`, not the number; callers that need it already have it keyed by `message_id`. Body is never echoed.

### 4.3 Query: `GET /v1/messages/{id}` returns `{message_id, state, state_updated_at, attempts[], events[] (paged), segments, cost, error}`. gRPC: `Get`, `WatchEvents(stream)`.

### 4.4 Error taxonomy (stable codes, same on REST (`application/problem+json`), gRPC status+details, and events)
| Category | Codes (examples) | HTTP | gRPC | Retryable |
|---|---|---|---|---|
| VALIDATION | INVALID_RECIPIENT, UNSUPPORTED_DESTINATION, BODY_TOO_LONG, INVALID_SENDER | 400/422 | INVALID_ARGUMENT | no |
| AUTH | UNAUTHENTICATED, FORBIDDEN_SENDER, FORBIDDEN_DESTINATION | 401/403 | UNAUTHENTICATED/PERMISSION_DENIED | no |
| CONFLICT | IDEMPOTENCY_KEY_REUSED | 409 | ALREADY_EXISTS | no |
| POLICY | RECIPIENT_OPTED_OUT, QUIET_HOURS, QUOTA_EXCEEDED, RATE_LIMITED | 403/429 | FAILED_PRECONDITION/RESOURCE_EXHAUSTED | rate/quota: caller backs off |
| PROVIDER_REJECT | CONTENT_REJECTED, SENDER_NOT_REGISTERED, NUMBER_UNREACHABLE, CARRIER_FILTERED | n/a (async) | n/a | no |
| PROVIDER_TRANSIENT | PROVIDER_TIMEOUT, PROVIDER_UNAVAILABLE, PROVIDER_THROTTLED | n/a | n/a | yes (budgeted) |
| EXPIRED | VALIDITY_EXPIRED | n/a | n/a | no |
| INTERNAL | INTERNAL | 500 | INTERNAL | yes |

Each adapter maps provider codes (e.g. Twilio 21610 -> RECIPIENT_OPTED_OUT, 21211 -> INVALID_RECIPIENT, 30003 -> NUMBER_UNREACHABLE, 30007 -> CARRIER_FILTERED, 429 -> PROVIDER_THROTTLED) with a golden-file test.

### 4.5 Provider ingress (not part of the platform contract)
`POST /v1/providers/{provider}/{route_id}/callbacks` and `.../inbound`: accept the provider's native encoding (Twilio: form-urlencoded), verify signature before any state change using the externally visible URL (configurable `public_base_url`), constant-time compare, support key rotation (list of active secrets per route), optional replay window, persist raw, enqueue, return 2xx. Webhook secrets and routes live in the secret store, not env vars. This is where #71's "signatures verified before state changes" lands.

## 5. Delivery state machine

States and rank (a transition is allowed only to a higher rank, or sideways within the same rank for the same terminal family; late lower-rank events are recorded in history but do not change state):

| Rank | State | Meaning |
|---|---|---|
| 10 | ACCEPTED | durable, not yet queued |
| 20 | QUEUED | on dispatch topic (not_before may delay) |
| 30 | SENDING | claimed by a dispatcher, provider call in flight (lease) |
| 40 | SUBMITTED | provider accepted (has `provider_message_id`) |
| 50 | SENT | handed to carrier (provider says sent) |
| 90 | DELIVERED | handset receipt (terminal) |
| 90 | UNDELIVERED / FAILED / REJECTED / EXPIRED / CANCELED | terminal failures (carrier or provider) |
| 95 | UNKNOWN_FINAL | no terminal report within SLA; reconciler gave up (terminal, flagged) |

Rules: `DELIVERED` after `SENT`-regression events is idempotent; a terminal failure followed by `DELIVERED` (rare carrier behaviour) is accepted once and flagged `late_correction`. Provider statuses map via adapter tables (`queued->SUBMITTED`, `sent->SENT`, `delivered->DELIVERED`, `undelivered->UNDELIVERED`, `failed->FAILED`, unknown -> recorded, no state change). `READ` and `RECEIVING` are not delivery states (RCS/inbound): drop from the outbound enum.

Protobuf: first value `STATE_UNSPECIFIED = 0`. Persist as text with a check constraint so new states do not need `ALTER TYPE`.

## 6. Idempotency, retries, DLQ, ordering

- **At the edge**: `(tenant_id, idempotency_key)` unique; same key and same `request_hash` returns the original; transaction writes message+outbox atomically. A client retry after timeout can never double-send.
- **Outbox -> Kafka**: at-least-once; key = `message_id` for events, `route_key` (= `provider_account|country|traffic_class`) for `sms.dispatch.v1` so per-route rate limiting is local to a partition owner; ordering of events per message is guaranteed by key `message_id` on `sms.events.v1`.
- **Dispatch exactly-once effect**: the conditional `QUEUED -> SENDING` update with lease is the claim; duplicate dispatch events lose the claim and are acked. The provider call carries `client_ref = message_id:attempt_no` (and the provider's idempotency token when supported). Provider outcomes: (a) accepted -> `SUBMITTED`; (b) definite reject -> terminal; (c) transient error before acceptance (connect error, 5xx before body, 429) -> schedule retry; (d) **ambiguous** (read timeout, connection reset after write) -> state stays `SENDING`, reconciler calls `lookup(client_ref)`; if the provider confirms nothing was created, a new attempt is made; if it cannot confirm by the reconcile deadline, the message is **resent, capped and counted, with an alert** (decision D6: a missed message is worse than a duplicate), and only within validity (`expires_at`, optional). No failover before reconciliation.
- **Retries**: attempt budget per class (OTP: 2 attempts within validity; transactional: 5 over 1 h; marketing: 3 over 6 h), exponential backoff with full jitter via delay topics (`sms.dispatch.retry.{1m,5m,30m}`) or `not_before` on the message, never `time.sleep` in a consumer.
- **Consumer acks**: commit offset only after the transaction that records the outcome; poison/deserialization errors go to `sms.dlq.v1` with headers (original topic/partition/offset, error, attempt count) after bounded retries; DLQ is alerting + replay tooling, not a silent sink. Disable auto-commit, `enable.auto.offset.store=false`, cooperative-sticky assignor, commit on revoke (this subsumes #69).
- **Producers**: `acks=all`, `enable.idempotence=true`, bounded `delivery.timeout.ms`, delivery result surfaced to the caller of the publish function (the relay); no producer calls on the request path.
- **Exactly-once claims**: none made. The platform guarantee is "at-least-once publication, effectively-once provider submission under non-ambiguous outcomes, ambiguity resolved by reconciliation, and a documented residual duplicate risk when a provider cannot look up by client reference".

## 7. Scaling model and bottlenecks

- Throughput levers: Kafka partitions of `sms.dispatch.v1` (start 12, key by route) x dispatcher threads per partition; Postgres write rate (messages + attempts + events + outbox ~ 6-8 row writes per message) is the first bottleneck: size for ~1k msg/s on a single primary, then partition tables by month and move `message_events`/`provider_events` to an append-optimised path.
- Provider limits are the true ceiling: Twilio per-number/messaging-service MPS (1 MPS long code, 3 MPS toll-free, higher for registered 10DLC/short code), account concurrency; hence the per-route token bucket in Redis (or Postgres advisory-lock-free in-process bucket partitioned by Kafka key ownership) and back-pressure by pausing consumption when the bucket is empty.
- API: stateless, scale horizontally; no blocking client calls on the event loop; request path does one DB transaction (target p99 < 50 ms at the DB).
- Outbox relay: single active leader per shard (`SKIP LOCKED` batches of 500), lag metric; fallback to CDC (ADR-2) if write amplification hurts.
- Reconciler and callback projector scale by `message_id` hash.
- Hot spots: callback bursts after campaigns (accept fast, enqueue, project asynchronously), `suppressions` lookup on every send (cache with negative TTL and invalidation by event), large marketing batches (batch endpoint writes in chunks; per-tenant fairness via weighted queues).

## 8. Security model

- **Authn/z**: service-to-service identity (mTLS via mesh or OIDC client-credentials JWT, audience `ujumbe`); roles `sender`, `reader`, `admin`; per-caller allow-lists of sender profiles, countries, traffic classes; Kafka ACLs per topic (producers of `sms.commands.v1` limited to platform principals). `/docs` off by default outside dev.
- **Secrets**: provider credentials and webhook secrets from a secret store (Vault/KMS/k8s secrets), versioned, rotatable without restart; `SecretStr` in settings; no defaults for credentials; startup refuses PLAINTEXT Kafka or default passwords outside dev.
- **Input**: E.164 normalization (phonenumbers, region hint), number-type check, destination allow-list, body length/segment cap, control-character stripping, metadata size limit; SSRF: callback URLs only from registered allow-listed hosts, https only, no private ranges, no redirects.
- **PII**: bodies encrypted at rest (application-level envelope encryption or at least column encryption for OTP class), recipient stored E.164 + HMAC; logs carry ids only; audit via `message_events` rather than the row-copy trigger; retention and erasure job; Kafka payloads carry hashes not numbers (4.2).
- **Abuse/cost**: per-tenant token buckets (requests/s, messages/day, spend/day), per-destination velocity limits, country allow-list, conversion-ratio anomaly detector (SMS pumping), kill switch per tenant and per route.
- **Webhooks**: verify-then-store, rotating secrets, rate-limited endpoints, no state change on failed signature, raw payload retention for forensics (PII-minimised).
- **Supply chain**: pinned and audited dependencies (pip-audit, Dependabot gated on green CI), image scan, non-root distroless-style image, read-only filesystem.

## 9. Observability and SLOs

Structured JSON logs (single sink, `message_id`, `correlation_id`, `tenant_id`, `route_id`, `attempt_no`, `recipient_hash`; never body), OpenTelemetry traces across API -> outbox -> Kafka headers -> dispatcher -> provider call, Prometheus metrics: `messages_accepted_total{tenant,traffic_class}`, `dispatch_latency_seconds` (accepted -> submitted), `provider_call_seconds{provider,outcome}`, `state_total{state}`, `outbox_lag_seconds`, `kafka_consumer_lag`, `dlq_messages_total`, `callback_signature_failures_total`, `circuit_state{route}`, `delivery_ratio{route,country}`, `spend_total`. Health: `/livez`, `/readyz` (DB, Kafka, secret store reachable), worker health endpoints with last-poll age.
Suggested SLOs (confirm with Q-UJU-06): API availability 99.9%/30d; accept latency p99 < 300 ms; OTP accepted -> submitted p95 < 3 s, p99 < 10 s; other traffic p95 < 60 s; zero acknowledged-but-lost messages (alert on any message in `ACCEPTED/QUEUED` > 5 min); delivery-report projection lag p99 < 30 s; provider-reported delivery ratio alert at -10% vs 7-day baseline per route.

## 10. Migration path from today's code

Order matters; each step ships behind existing behaviour.
0. Baseline: green CI, runnable env, red tests fixed, Dockerfile fixed (phase 0).
1. Stop the bleeding without redesign: UJU-008 (id), UJU-009 (response mapping), #68/PR #75, #67/PR #74 (with changes), #69, Kafka security/producer fixes, stub-mode default, auth and rate limits at the edge.
2. Introduce `messages`/`outbox`/`message_events` tables alongside `sms`/`sms_responses` (expand). Dual-write for one release (API writes both), backfill `messages` from `sms` + `sms_responses`; add idempotency key; drop content unique constraint (#70).
3. Move dispatch to claim-with-lease, add reconciler, add timeouts/circuit breaker; switch event emission to the outbox; keep old topics running in parallel (`SmsReceived/Submitted/Sent` remain published for one deprecation window; new `sms.events.v1` introduced).
4. Callback ingress + projector (#71); close PR #11; define the state machine; introduce `DeliveryProvider` port and refactor Twilio into an adapter (#72 slices); add second provider behind the router.
5. Inbound MO + suppression; sender profiles; quotas; PII retention; remove old tables/topics (contract) after consumers (niosys) move.
Compatibility: protobuf additions only (optional fields) until the old topics are retired; `buf breaking` gate; consumers before producers on every deploy (as required for #74).

## 11. ADR-worthy decisions

| ADR | Question | Options | Recommendation |
|---|---|---|---|
| ADR-1 | Contract format and transports | (a) protobuf + registry on Kafka, JSON on REST, gRPC from same .proto; (b) JSON + CloudEvents everywhere; (c) keep current ad hoc | (a) with a CloudEvents-compatible header set (id, type, source, time, correlation) so non-protobuf callers can interoperate; one `.proto` repo shared by all three services |
| ADR-2 | Outbox publication | (a) polling relay with SKIP LOCKED; (b) CDC (Debezium) | (a) now (no new infra), revisit (b) at >2k msg/s or when ops already run Debezium |
| ADR-3 | Provider failover | (a) active-passive per route with circuit breaker; (b) weighted least-cost routing; (c) no failover | (a) first; failover only on definite pre-acceptance failure; (b) later once cost data exists |
| ADR-4 | Runtime/framework | (a) stay Python/FastAPI on 3.12 with pydantic v2/SQLAlchemy 2; (b) rewrite in Go/Kotlin | (a): the problem is design and hygiene, not language; revisit only if load tests show the Python dispatcher cannot meet the target |
| ADR-5 | Kafka client model | (a) thin in-house loop on confluent-kafka (explicit ack, DLQ); (b) FastStream/Faust-style framework; (c) per-message threads | (a) for control over commit semantics; extract a reusable consumer kit shared with barua-pepe |
| ADR-6 | State storage for rate limits/dedupe cache | Redis vs Postgres-only | Redis for token buckets (loss-tolerant), Postgres for anything needing durability (idempotency, suppression) |
| ADR-7 | Consent/opt-out ownership | (a) niosys owns consent, ujumbe enforces provider-level suppression and reports; (b) ujumbe owns all | (a): marketing consent and preferences belong to niosys; STOP/HELP and carrier compliance are channel-specific and must act at the gateway even if niosys is down |
| ADR-8 | Message body at rest | plain / column-encrypt / do not persist after dispatch (OTP) | encrypt bodies, purge OTP bodies after terminal state + short TTL; keep length/segments/encoding only |
| ADR-9 | Status enum persistence | PG native enum vs text+check | text + check (rollout-safe) |
