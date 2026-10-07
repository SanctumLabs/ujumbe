> **Status: Proposed. Discovery output dated 2026-10-07; not accepted architecture.** Describes the code as inspected on that date and a proposal for its replacement. Decisions are tracked in the ADR index and open-question log.

# ujumbe: PR review and assessment of existing issues

Nothing in this file has been posted to GitHub. Sources: `mcp__github__pull_request_read` (get, get_files, get_diff, get_review_comments,
get_reviews, get_comments, get_check_runs, get_commits), job logs, GitHub Actions run list, and the code on `develop` @ `6b097ec`.
I also fetched `pull/74/head`, `pull/75/head`, `pull/11/head` into a scratch clone and ran the unit suite on each (Python 3.11, locked deps,
psycopg2-binary substituted). Baseline `develop`: **10 failed, 57 passed, 2 skipped**.

Summary

| PR | Verdict | One line |
|---|---|---|
| #74 `fix(sms): allow provider-managed senders` (fixes #67) | **Merge after changes** | Right layer and tests are real, but it silently removes the only duplicate guard for senderless rows, ships an irreversible migration, never proves the messaging-service path is configured, and needs a rollout order |
| #75 `refactor: streamline SMS submission handling in consumer` (fixes #68) | **Merge after changes** (small, merge soon) | Correct fix for the double publish; its test cannot fail if the bug returns, and it does not meet #68's own worker-level acceptance criterion |
| #11 `Track Delivery status of SMSes` (draft, 2023) | **Close**, supersede with #71 | 140 files, 26 commits, unmergeable base, replaces the Kafka stack with a private package, callback endpoint unauthenticated and not Twilio-compatible, consumer is a copy of the wrong worker |

Neither #74 nor #75 changes the 10 pre-existing unit failures (identical set before and after). #74 adds 7 passing tests, #75 replaces 1 skipped test with 1 passing test.
`#74 + #75` merge cleanly into one tree (trial merge on `develop`: no conflicts, 17 files, +166/-37; they touch disjoint files).

---

## PR #74 `fix(sms): allow provider-managed senders` (branch `codex/fix-67-optional-sender` -> `develop`)

Author BrianLusina, 1 commit `c9100fd`, 14 files, +153/-11, opened 2026-10-05. Labels `bug, documentation, enhancement`; not draft; `mergeable_state: blocked`.

**Does it fix #67 and only #67?** It fixes the broken half (event and persistence contracts): producers omit `sender` when absent
(`sms_received_producer.py`, `sms_submitted_producer.py`, `sms_sent_producer.py`), consumers map an empty sender to `None`
(`sms_received_consumer.py:42`, `sms_submitted_consumer.py:39`), mapper and model allow NULL, migration `cbf76f4c2bde` relaxes the column. Scope is clean: no
unrelated changes. Gaps against #67's own acceptance criteria:
- "A request with only recipient and message is accepted and dispatched through the messaging service": the Twilio branch already existed
  (`sms_client.py:67-72`, tested at `tests/unit/infra/sms/test_sms_client.py:91`), but `twilio_messaging_service_sid` defaults to `""`
  (`settings.py:41`) and is absent from `.env.example`. A senderless message with no configured service now travels the whole pipeline
  and fails at Twilio (or "succeeds" in stub mode, UJU-026). No validation anywhere.
- "Provider-neutral originator policy": not attempted (acceptable, belongs with #72), but #67 should have been split so this PR could close it.
- "Tests cover both flows": the PR tests mappers, producers and consumers in isolation. There is no test through the API route or the
  worker (the API test base is red on `develop`, UJU-029) and the DB integration tests (testcontainers) were not extended and cannot run here.

**Right layer / abstraction?** Right layer (event adapters and persistence), wrong shape. Five copies of
`data_attributes = dict(...); if sms.sender: data_attributes["sender"] = ...; Sms(**data_attributes)` are copy-pasted. Verified: the protobuf
constructor already treats `None` as unset (`Sms(sender=None).HasField("sender") is False`), so `sender=sms.sender.value if sms.sender else None` is enough, and a single
`Sms <-> proto` mapper would remove all five copies (this is what #72's canonical envelope will replace anyway). Consumers use truthiness; an explicit
empty string is conflated with "absent" while the producer (via `HasField`) distinguishes them. Use `data.HasField("sender")` for symmetry.

**Regression, race, idempotency, ack ordering:**
1. **Duplicate guard regression (both bots flagged it, I agree).** Unique `(sender, recipient, message)` (`sms_model.py:22-29`) no longer protects rows with
   `sender IS NULL` (PostgreSQL treats NULLs as distinct). This is the only content-level duplicate check in the system. Also the constraint is wrong in the first place
   (it rejects legitimate repeats, #70), so the right move is not to add a partial unique index (that would re-impose the #70 bug on the new path) but to
   make the decision explicit: state in the PR that content uniqueness is being retired, rely on `identifier` uniqueness today, and let #70 replace it with an idempotency key.
   Note the interplay with UJU-008: all API-created ids collide anyway, so today the practical guard is the shared id.
2. **Rollout order.** Old consumers do `PhoneNumber(data.sender)`: an absent sender yields `""` and `ValueError` -> logged, skipped, auto-committed (data loss, #69). The API only produces senderless events after this
   change, so deploy order must be migration -> consumers (both workers) -> API/producers. The PR description has no mention of this.
3. **Migration `cbf76f4c2bde`.** `ALTER COLUMN ... DROP NOT NULL` is metadata-only and safe online. Down-revision `0ad6b839a7f9` is the current single head, so no branch.
   `downgrade()` raises `NotImplementedError`; CodeRabbit's suggestion (check for NULLs, restore NOT NULL only if none) is cheap and correct. The initial migration's own downgrade is
   already broken (UJU-024), so this is not a blocker.
4. No change to ack ordering (consumers unchanged apart from the sender line).

**Tests: do they test behaviour?** Yes, better than average: producer tests inspect the produced protobuf (`HasField("sender")` false), consumer tests build a real protobuf
without sender and assert the domain object has `sender is None`, mapper tests cover both directions. Weaknesses: `SmsSent` test builds an entity with status PENDING and asserts only sender
(fine), the consumer tests mock the Kafka client so deserialization against the registry is not exercised, nothing asserts the `messaging_service_sid` call is made for a senderless
event end-to-end, no DB-level test that two NULL-sender rows with equal content behave as intended.

**Base branch and scope:** correct (`develop`), single concern. Metadata nit: label `documentation` and the ticked checklist "I have made corresponding changes to the documentation" are not true
(no docs changed); "How can we test this?" is the untouched template.

**Conflicts with the other PR / target design:** none with #75 (disjoint files). Consistent with #70/#71/#72: it makes the contract tolerate absence, which any redesign needs. It will be
superseded mechanically by the canonical envelope in #72; keep it small so that is cheap.

**CI:** `Lint (3.10)` **failure**, CodeQL, GitGuardian, Analyze (python/actions) success. The lint failure is not caused by the PR: it is the repo-wide
`poetry install` error "No file/folder found for package ujumbe" that fails every `develop` push too (runs #146, #148, #150, #153, #154). No test job exists, so no check ran the tests.
Review threads: CodeRabbit (2, partial index and downgrade) and Codex (1, same partial-index point), all unresolved, no human review.

**Verdict: merge after changes.** Required before merge:
1. Resolve the NULL-sender uniqueness thread explicitly (recommended: leave the constraint as is, add a line in the PR and a reference to #70; do not add a partial index).
2. Fail fast when a senderless request cannot be dispatched: validate at startup (or at submit) that `TWILIO_MESSAGING_SERVICE_SID` is set whenever senderless requests are allowed; add `TWILIO_MESSAGING_SERVICE_SID` to `.env.example`; test the senderless path from consumer event to `SmsClient.messages.create(messaging_service_sid=...)`.
3. Make `downgrade()` conditional on no NULL senders (do not leave `NotImplementedError`).
4. Replace the five `dict` blocks with `sender=... if sms.sender else None` or one mapper function; use `HasField` in consumers.
5. Add the rollout order to the PR description; remove the incorrect `documentation` label/checklist claim.
6. Keep `#67` open (or edit it) for the originator-policy half and move that half under #72.
Optional but good: an integration test (Postgres) inserting two senderless rows with equal content to document the new behaviour.

---

## PR #75 `refactor: streamline SMS submission handling in consumer` (branch `codex/fix-68-single-submission-event` -> `develop`)

1 commit `c369197`, 3 files, +13/-26, opened 2026-10-05 07:11. Labels `bug, enhancement, Consumers`; `mergeable_state: unstable` (failing lint check). No review comments (CodeRabbit and Codex both rate-limited: "Review limit reached", "usage limits"), no human reviews.

**Does it fix #68 and only #68?** The production change is the right and minimal fix: `CreateSmsService.execute` already does `repository.add` then
`producer.publish_message(sms)` (`app/domain/sms/create_sms.py:25-26`, with `SmsSubmittedProducer` injected in `domain_container.py:21-25`), so the worker's second `sms_submitted_producer.publish_message(sms)` was a duplicate and is
removed. Verified by reading both call sites. Downstream effect of the bug: `SmsSubmittedConsumer` receives two events with the same id and `SendSmsService` calls Twilio twice (a charge and a second
text to the recipient). Scope is tight; the only extras are the added module-level function `create_submitted_sms` and the `assert_called_once_with` tightening in `test_create_sms.py`.

**Right layer / abstraction?** Right owner (the use case owns persist-and-submit). `create_submitted_sms(sms, create_sms_svc)` is a pass-through that wraps a single call (`create_sms_svc.execute(sms)`); it exists only to let the test import something and adds an
untyped parameter (`sms`) and a docstring that restates the call. It should be deleted, or replaced by a real extraction of the loop body (see tests). Left unchanged: the stale docstring/log wording ("proceeds to create the SMS record"), and the
`while True` loop that swallows every exception (UJU-014).

**Regression, race, idempotency, ack ordering:**
- No new regression; the removed publish is strictly redundant. Order stays: poll -> persist+commit -> publish -> `commit()`.
- It does **not** meet #68's second acceptance criterion in any meaningful way. After this PR, a crash between the DB commit and the publish loses the message permanently: on redelivery `repository.add` raises `IntegrityError`
  (unique `identifier`), `CreateSmsService` turns it into `CreateSmsException`, nothing is published. Conversely a crash after publish but before ack cannot double-publish only because the insert fails again. The "fixed" behaviour is therefore at-most-once by accident, not exactly-once. This is #70's dual-write problem and must not be reported as solved.
  When #70 makes persist idempotent (treat existing row as success and republish), duplicates of `SmsSubmitted` become possible at-least-once, so the sender must dedupe by message id (see `03-target-design.md`); a consumer-side dispatch claim is the real exactly-once boundary.
- Ack: `commit()` is still broken (#69), so after this PR processing still depends on auto-commit; the PR neither helps nor hurts.
- Pre-existing, hit by this path: UJU-008 (shared id) makes the second message from an API process fail at the insert, so the fix cannot be observed end to end until that is fixed.

**Tests: do they test behaviour?** No, the new test cannot catch the bug it targets. `test_creates_and_submits_sms_once` calls the pass-through helper with a `Mock(spec=CreateSmsService)` and asserts `execute` was called once: it passes
whether or not `main()` still publishes a second event, because `main()` is never invoked and no producer is wired. #68 asked for "a worker-level test asserts one input record yields exactly one submitted event". The PR also **deletes** the existing (skipped) test of `main()` instead of fixing why it could not exit the loop.
`assert_called_once_with` in `test_create_sms.py` is a legitimate, tiny strengthening (it checks the use case publishes once, which is the property now relied on).

**Base branch and scope:** correct. Title says "refactor" while the change is a bug fix (`fix:`), which matters for semantic-release/changelog if it is ever enabled.

**Conflicts:** none with #74 (trial merge clean). With #70: `CreateSmsService` will be rewritten to write an outbox row instead of publishing, and the worker will call it once as it does after this PR, so the PR is on the target path; the helper function would be dead after #70.

**CI:** same single failure as #74 (`Lint (3.10)`, repo-wide poetry install error, not PR-induced); CodeQL, GitGuardian, Analyze success. Local run: 58 passed / 10 failed (the same 10 as `develop`) / 1 skipped.

**Verdict: merge after changes (small; this is a P0 duplicate-charge fix, merge promptly).**
1. Delete `create_submitted_sms`; instead extract the loop body into `process_one(consumer, create_sms_svc)` (or keep inline) and write a worker-level test using the **real** `CreateSmsService` with a fake repository and a fake producer: feed one `SmsReceived` record, assert exactly one `publish_message` call on the submitted producer and exactly one `commit()` call, and a second case where `execute` raises and `commit()` is not called.
2. Retitle to `fix(consumer): publish submitted event once per received message`.
3. Do not close #68 as "exactly once" on merge; add a comment that retry-safety depends on #70, or keep the retry criterion open there.
4. Do not remove the previously skipped test without replacing its intent.

---

## PR #11 `Track Delivery status of SMSes` (draft, `feat/sms-status-callback`, created 2023-06-09, last updated 2023-11-02)

140 files, 26 commits, +4,884/-2,488. Base `455f1e0` (2023); `mergeable_state: dirty`; no check runs, no reviews, no comments. Labels documentation/enhancement/tests/Consumers. Local history is shallow so I could not compute the merge-base against current `develop`; GitHub reports conflicts.

**What it tries to do and what it actually contains.** The description promises one webhook endpoint plus consumer. The diff additionally: replaces the whole in-repo Kafka stack with a private package
(`eventmsg-adaptor` from a GitLab PyPI index and `sanctumlabs-messageschema`, `pyproject.toml` hunk), deletes `app/infra/broker/kafka/*`, `app/messages/*` and `buf.gen.yaml`, moves modules (`app/domain/sms` -> `app/domain/services/sms`, `app/services` -> `app/adapters/...`),
migrates to pydantic v2, bumps Python to `^3.11`, adds OpenTelemetry/Sentry/boto3/aiokafka/injector dependencies, and pastes a CORS block containing another company's origins (`settings.py` hunk). None of that is related to delivery tracking.

**Does it work or fit?**
- Endpoint `POST /api/v1/sms/callback` takes a JSON body model `SmsCallbackRequestDto{AccountSid, From, MessageSid, MessageStatus, SmsSid, SmsStatus}` (`app/api/sms/dto.py`, `routes.py` hunk). Twilio posts `application/x-www-form-urlencoded`, so a real callback would be rejected with 422.
  There is **no signature verification** and no authentication: anyone can forge delivery statuses. `routes.py` also has `if e is AppException:` (always false) so every error is returned as a 400 with the exception text.
- The consumer `SmsCallbackReceivedConsumer` is a pasted copy of the SMS consumer (`recipient = PhoneNumber(data.account_sid)`, constructs `SmsCallback(recipient=..., message=..., status=...)` with fields the entity does not have); the worker `sms_callback_received/__main__.py` is a copy of the **received** worker (consumes `SmsReceived`, creates SMS, publishes `SmsSubmitted`) and never touches callbacks.
- `CreateSmsCallbackService` calls `repository.add` on a repository typed `SmsRepository`; the DB repository correlates by `SmsSid` through `sms_responses.sid` (a reasonable idea) but upserts by `message_sid` with no state ordering (a late `sent` after `delivered` regresses the status), no history, no unknown-callback path ("handled in another PR").
- The endpoint is `async` and `await`s a producer whose underlying Kafka client call blocks (same problem as UJU-012), and the PR adds tracing spans around the route but no trace propagation into events.
- No CI ever ran on it.

**Does it conflict with the target design?** Yes, fundamentally: it assumes the external event library and schema package that `develop` deliberately does not use; #70 (outbox), #71 (idempotent, monotonic, authenticated callback projection with history) and #72 (provider-neutral events) invalidate its data model (`sms_callbacks` stores Twilio field names; `unique(account_sid, sender, message_sid, sms_sid)`).

**Verdict: close** (as superseded by #71; do not rebase). Rebasing is not viable (140 files, base two-and-a-half years old, structural moves, different broker stack). Salvage, as ideas only, into #71's description: (1) correlate callbacks via provider message id stored in `sms_responses.sid` (already unique on `develop`);
(2) the field list of Twilio status callbacks (`MessageSid`, `MessageStatus`, `SmsSid`, `SmsStatus`, `AccountSid`, `From`, plus `To`, `ErrorCode`, `ErrorMessage` which it omits); (3) its test cases for duplicate/unknown callbacks, rewritten against the new design. Suggested closing note when the orchestrator decides to comment: "Superseded by #71; the branch predates the current architecture (unmergeable, replaces the Kafka stack, unauthenticated JSON webhook)". Delete the branch afterwards.

---

## Assessment of existing issues #67 to #73

Facts: opened 2026-10-04 by `ratholos` within four minutes of each other, **no comments, no labels, no assignees, no milestone, no parent/epic, no closed issues in history**. All seven carry real file:line evidence and I verified each claim against the code. Quality is high on diagnosis; weak on triage metadata and a few scoping choices.

| # | Correctly scoped? | Priority I would set | Sufficient? What is missing |
|---|---|---|---|
| #67 sender optional | Mixed: AC1-3 are small and done by PR #74; the "provider-neutral originator policy" sentence belongs to #72 | P1 | Needs: validation that a messaging service is configured, rollout order, decision on NULL uniqueness (#70). Split the policy half into #72 / UJU-021 |
| #68 exactly-once publish | Yes, precise root cause | **P0** (duplicate provider send and charge) | AC2 ("retry does not create a second provider submission") cannot be satisfied by the worker change alone; it needs #70 plus dispatch-side dedupe (claim-before-send). PR #75 does not test AC3. |
| #69 ack after success | Yes | **P0** (silent message loss) | Also needs: producer-side delivery guarantees (UJU-012), SASL/TLS wiring (UJU-011), poll-error handling, rebalance/shutdown commit, `max.poll.interval` vs slow provider (UJU-013/014). "Kafka integration tests without skips" requires #73 and a working Docker/Testcontainers pair (docker-py 6 vs requests 2.33). Retry/DLQ design is one sentence; deserves its own design |
| #70 outbox + idempotency | Correct but too big: bundles outbox, relay, client idempotency key at API, constraint removal and provider idempotency | **P0** | Split into (a) idempotency key + drop content-unique constraint, (b) outbox table + relay, (c) consumer-side dispatch claim/inbox and provider reconcile. Missing: the **provider call is the real non-transactional boundary**, so a `SENDING` claim with lease and reconcile-by-client-reference is required for ambiguous timeouts. Depends on UJU-008 (shared id) which makes identity meaningless today |
| #71 callbacks | Right problem, large | P1 | Missing: the send path never requests callbacks (`status_callback`, `sms_client.py:62-72`); Twilio form-encoded payload and signature URL handling behind proxies; state-machine definition (UJU-023); the crash that stops any response from being recorded (UJU-009); an outbound `DeliveryReported` event contract toward niosys; unknown-callback parking and reconciliation job; PR #11 disposition |
| #72 provider-neutral redesign | Over-scoped for one issue ("deep module" owning validation, idempotency, routing, persistence, outbox, projection, correlation) and mentions MMS/SMMS/inbound, which the SMS gateway role in the platform may not need | P2 (after P0/P1) | Decompose: canonical envelope/contract, `DeliveryProvider` port + Twilio adapter, router/failover, second provider, inbound MO. Missing acceptance criteria for failover, rate limits, credentials/rotation, capability negotiation errors. Risk of a rewrite stalling fixes; sequence behind #68/#69/#70 |
| #73 test environment | Correct and necessary | **P1, first in line** | The stated cause (3.14) is only one failure mode: gevent 23.9.1 does not build on 3.13; `psycopg2` source build needs headers (use `-binary` or psycopg 3); CI `poetry install` fails on the missing package dir **independent of Python** (so even 3.10 is red today); pylint exits 30; the unit suite is red (10) on a working interpreter; docker-py 6.0.1 breaks with requests 2.33; Python 3.10 itself reaches EOL this month. Acceptance "clean install and pytest succeed" is unreachable until these are fixed (UJU-028, UJU-029) |

**What is missing from the set altogether** (filed as new issues, all referencing these): shared `Sms` id bug (UJU-008), provider-response mapping crash (UJU-009), no authn/z and no rate limits/quotas (UJU-010, UJU-022), Kafka TLS/SASL not applied (UJU-011),
producer delivery blindness and event-loop blocking (UJU-012), provider timeouts/error taxonomy/circuit breaker (UJU-013), worker lifecycle (UJU-014), PII in logs/audit (UJU-015), API/event contract and error semantics (UJU-017), phone/encoding/segment handling (UJU-018/019),
opt-out and compliance (UJU-020/021), state machine (UJU-023), migration safety and schema (UJU-024/025), stub-mode defaults (UJU-026), deployment artefacts (UJU-027), CI and test-suite repair (UJU-028/029), provider routing/failover/credentials (UJU-033), observability (UJU-016).

**Process observations (for the orchestrator, no action taken):** the repo has branch protection on `develop` but its only workflow has failed on every push since at least run #146 while Dependabot merges continued; PR bots rate-limited on #75, so it has had no automated review; PR template checkboxes are ticked in both PRs without being true;
issues have no labels so none of the repository's triage tooling applies.
