# Pre-live review — Liability Cascade

Reviewed 2026-10-20 against `docs/DESIGN.md`, the original brief, and `docs/PHASE2_HANDOFF.md`. The owner authorized review and Phase 3 after the historical Phase 2 stop.

## Result

PASS for the reviewed local requirements. No production-code defect was found in the consensus-binding, deterministic attribution, authorization, accounting, or exactly-once settlement paths. The contract source remains SHA-256 `b5118d6cd32ef3a642795b4e046fa0bdc13b9f60960fd900833d7e80962dff40` (Git blob `53ff0f7eb7b7be57115886476c55e282b8ab3492`). This is a code review and local verification result; live consensus is recorded separately.

## Reviewed boundaries

- `adjudicate.validator_fn` rejects non-return/error candidates, validates the complete envelope, independently invokes `_assess` across every configured step, and compares complete canonical JSON. There is no ignored stored nondeterministic field or citation exception. Snapshot hashing binds the deployment address, frozen configuration, report, recordings, and activated ledger.
- The model returns only one local verdict. Code derives evidence availability/tampering, effective verdicts, earliest-fault attribution, status, payer, full-bond amount, refunds, and settlement receipt. Model-supplied payer/status/amount fields are rejected.
- Every constructor/write reaches `_save`, which checks per-owner conservation, bounded nonnegative integer ledger amounts, activation locks, one full-bond slash at most, total award equality, and assessment/settlement latches before persisting. All terminal writes revert. Timeout settlement needs no network/model work.
- The actual validator callback captured from `adjudicate` is invoked by `VMContext.run_validator` through the test-only compatibility shim. A new spy test proves independent assessment runs when a schema-valid forged candidate preserves the final payer but changes a downstream verdict.

## Changes made during review

The production source required no changes. The previous adversarial tests sampled the envelope rather than covering every leaf and did not test unequal bonds at the maximum amount. Added 75 regression cases:

| Added test | Cases | What it proves |
|---|---:|---|
| `test_review_every_stored_consensus_leaf_is_bound` | 68 | Every envelope/step/observation leaf is bound; actual callback rejects each changed field and accepts the original; persisted bytes stay unchanged |
| `test_review_valid_foreign_snapshot_cannot_be_replayed` | 5 | Self-consistent candidates bound to another contract, pipeline, claimant, recording timestamp, or bond configuration cannot replay into this snapshot even with the same ultimate payer |
| `test_review_valid_forged_same_payer_requires_independent_work` | 1 | The real callback performs independent assessment and rejects a valid-shaped downstream verdict forgery despite identical allocation |
| `test_review_unequal_and_maximum_bonds_conserve_exact_integers` | 1 | Bonds 1, 10**18, and 7 settle with award 10**18 and refunds 8; exact integer conservation and replay rejection |

Existing tests cover wrong callers, every configured operator's claimant exclusion, immutable records, second report/adjudication, every terminal write, deadline boundaries, funding cancellation, malformed model results, independently changed evidence, unavailable/tampered/missing logs, and early uncertainty barriers.

## Reverification

Pinned interpreter: `C:\Users\User\Desktop\Genlayer apps\intelligent-contracts-v2\.venv\Scripts\python.exe`.

`tools/verify_local.py` passed: **193 tests, 0 failures, 0 errors, 0 skipped; 3 AST lint checks passed; 1 successful SDK semantic validation; 7 public methods (5 writes, 2 views)**. One informational `I200` notice says a newer runner exists; the approved exact runner stays pinned. Current outputs are under `verification/`. The original handoff's 118-test count remains the historical Phase 2 result.

## Limits retained for live reporting

Synthetic deposit/award units have no token custody. A committed hash does not authenticate execution or prove adjacent handoff continuity. Unavailable evidence before the first proven fault can block attribution; timeout refunds remain the liveness path. Excluding operator addresses does not prevent an affiliated unconfigured claimant. URL admission validates syntax, not DNS/redirect publicness; this release uses only exact commit-pinned HTTPS paths at `raw.githubusercontent.com`, and claims no general SSRF/redirect guarantee. Direct tests use mocked model/web responses and the legacy SDK shim; live hosted-runner execution and votes require separate evidence.
