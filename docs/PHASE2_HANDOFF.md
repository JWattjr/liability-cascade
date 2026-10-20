# Phase 2 handoff - Liability Cascade

Date: 2026-10-20 (Africa/Lagos). Status: **PHASE 2 COMPLETE; STOPPED BEFORE PHASE 3**.

## Verified implementation

- Implementation commit: `326cb6dde532e3e64cd45fce8d2ab68f9d9a1e39` (local only).
- Contract Git blob: `53ff0f7eb7b7be57115886476c55e282b8ab3492` at `contracts/liability_cascade.py`.
- Contract SHA-256: `b5118d6cd32ef3a642795b4e046fa0bdc13b9f60960fd900833d7e80962dff40`.
- This handoff is added by a subsequent documentation-only local commit. The SHA above identifies the tested source and its verification evidence; this file cannot contain the SHA of the commit that first contains itself. Use `git log -1 --format=%H -- docs/PHASE2_HANDOFF.md` for that handoff commit. The contract blob must be unchanged between the two commits.
- Repository location: `C:\Users\User\Desktop\Genlayer apps\intelligent-contracts-v3\liability-cascade`.
- No remote configured, push performed, remote repository created, deployment sent, account key fetched, or Portal action taken for this Phase 2 delivery.

The approved amendment is implemented and reflected in `docs/DESIGN.md`: `report_failure` rejects every configured operator address. An independent address can still report. An operator's unconfigured affiliated address is not excluded by this address check.

## Exact verification results

| Check | Result |
|---|---|
| Pytest direct-mode suite | **118 passed, 0 failures, 0 errors, 0 skipped**; 36 test functions expanded by parametrization |
| `genvm-lint check --json` AST checks | **3 passed, 0 failures** |
| SDK semantic validation | **1 successful validation**, `ok=true`; 5 constructor parameters, 7 public methods: 5 writes and 2 views |
| Linter informational warning | **1**, code `I200`: a newer runner is available; the exact approved runner remains pinned |
| ABI/schema extraction | PASS; exactly the seven public methods listed below; all writes nonpayable |
| Header and line endings | Exact approved first line; `.gitattributes` is `* text=auto eol=lf`; checked files contain UTF-8 and LF bytes, without CR characters |

See `verification/phase2-results.json`, `verification/pytest.xml`, `verification/pytest.stdout.txt`, `verification/lint.stdout.txt`, `verification/lint.stderr.txt`, and `verification/schema.json`. The linter's online latest-version lookup was unavailable and it used its existing local GenVM cache; lint and SDK validation both succeeded. No toolchain was upgraded.

Runtime: Python **3.14.2**, `genlayer-py` **0.19.0rc2**, `genlayer-test` **0.30.0rc2**, `genvm-linter` **0.11.1rc2**, pytest **9.1.1**. All verification uses the existing interpreter at `C:\Users\User\Desktop\Genlayer apps\intelligent-contracts-v2\.venv\Scripts\python.exe`. Direct tests load SDK **v0.6.0-rc5** through the inherited Windows/legacy-SDK compatibility shim in `tests/conftest.py`; that test-only SDK selection does not alter the contract's pinned dependency header.

Reproduce from this repository root:

```powershell
& 'C:\Users\User\Desktop\Genlayer apps\intelligent-contracts-v2\.venv\Scripts\python.exe' tools/verify_local.py
```

The verification script runs lint before tests, extracts the schema, verifies the exact header and LF files, and writes the result artifacts. Direct tests run the leader locally with mocked web/model responses. Captured validator callbacks are then explicitly invoked with independent mocked fetches and judgments, including forged leaders. This exercises the real comparison callback, but is not proof of distributed consensus or hosted GenVM execution.

## Public signatures

Constructor (not a callable post-deployment method):

```python
LiabilityCascade(
    pipeline_id: str,
    charter: str,
    steps_json: str,
    recording_deadline: int,
    adjudication_deadline: int,
)
```

`steps_json` is an ordered JSON array of 2-5 objects, each containing exactly `step_id`, `operator`, `duty`, and `bond_units`. Deadlines use UTC Unix seconds. Each operator is distinct.

| Access | Exact signature | Meaning |
|---|---|---|
| Write, nonpayable | `deposit(amount_units: int) -> None` | Sender's bounded synthetic deposit; final fully funding deposit locks all bonds atomically |
| Write, nonpayable | `record_step(step_id: str, input_url: str, output_url: str, input_digest: str, output_digest: str) -> None` | Assigned operator records once before R |
| Write, nonpayable | `report_failure(final_output_url: str, description: str) -> None` | Nonoperator opens the sole incident during `[R, J)` |
| Write, nonpayable | `adjudicate() -> str` | Permissionless assessment; returns `PIPELINE_FAULT`, `NO_PIPELINE_FAULT`, or `UNATTRIBUTABLE` |
| Write, nonpayable | `settle_deadline() -> None` | Permissionless deterministic funding cancellation or deadline refund |
| View | `get_state() -> dict` | Configuration, state, recordings, incident, assessment, ledger, receipt, effective time window |
| View | `get_accounting() -> dict` | Synthetic unit, global/per-owner totals, conservation flag, refund/claimant-credit projections |

Every write reverts after any terminal state. Both views remain usable. `UNATTRIBUTABLE` is an outcome first stored in nonterminal `AWAITING_REFUND`; bonds remain locked until a timeout caller settles at or after J.

## Requirement-to-test coverage

All test names below are in `tests/test_cascade.py`. Parametrizations are part of the named test. `Pipeline.write` checks global/per-owner accounting after every successful write; `Pipeline.rejected` checks byte-equivalent parsed state and accounting after each rejected call. Delivery-only properties use `tools/verify_local.py` and Git checks rather than tests of a mock Git implementation.

| Design requirement | Test or verification covering it |
|---|---|
| Sections 1-2: one immutable pipeline, one incident, no administrative policy/payer override | `test_partial_deposits_activate_atomically_and_configuration_stays_frozen`; `test_report_frozen_description_not_in_semantic_prompt`; schema inventory in `tools/verify_local.py` |
| Pipeline ID/charter bounds, future ordered integer deadlines, bounded steps JSON | `test_constructor_configuration_bounds` |
| Exactly 2-5 unique step IDs and distinct nonzero operator addresses; strict fields and bounded duties/bonds | `test_constructor_step_constraints`; `test_pipeline_minimum_and_maximum_step_counts` |
| Frozen runner and actual supported persistent storage/public interface | `tools/verify_local.py` header check; 3 AST checks and successful SDK semantic validation; schema extraction |
| Synthetic units only, no payable public writes or real asset transfer API | Nonpayable flags and exact public-method inventory in `verification/schema.json`; `test_partial_deposits_activate_atomically_and_configuration_stays_frozen` |
| Funding starts empty; only configured sender deposits to its own capped ledger | `test_partial_deposits_activate_atomically_and_configuration_stays_frozen`; `test_invalid_deposits_revert`; `test_deposit_cap_and_unfunded_cancellation` |
| Full funding atomically moves all available units to locked before recording; no excess or later deposits | `test_partial_deposits_activate_atomically_and_configuration_stays_frozen`; `test_deposit_cap_and_unfunded_cancellation` |
| Incomplete funding can cancel/refund actual deposits at R without blaming absent records | `test_deposit_cap_and_unfunded_cancellation`; `test_all_terminal_writes_revert_and_views_survive[unfunded-*]` |
| Section 3: named operators can record only their own slot; claimant and timeout/adjudication roles separated | `test_operator_authorization_duplicate_and_independent_recording_order`; `test_configured_operator_cannot_claim`; `test_adjudication_requires_report_and_enforces_both_time_boundaries` |
| Section 4: record before R; report at R; adjudicate during `[R,J)`; report/adjudicate at J rejected | `test_record_at_or_after_deadline_reverts`; `test_configured_operator_cannot_claim`; `test_report_and_adjudicate_at_J_denied_timeout_allowed`; `test_adjudication_requires_report_and_enforces_both_time_boundaries` |
| Effective time windows are visible without automatic state transitions | `test_effective_time_window_without_automatic_state_transition` |
| Successful assessment is once-only, including unattributable outcomes; successful terminal settlement once-only | `test_earlier_uncertainty_blocks_later_fault_until_deadline`; `test_awaiting_refund_accepts_only_timeout_and_preserves_vector`; `test_all_terminal_writes_revert_and_views_survive`; `test_receipt_binds_accounting_assessment_and_config_once` |
| Failed model/consensus work does not consume assessment latch or mutate state | `test_malformed_model_cannot_become_unclear_or_mutate_state`; `test_model_invocation_failure_and_consensus_rejection_rollback` |
| Deadline refund needs no web/model calls and works without report or assessment | `test_no_report_timeout_cannot_be_called_early_and_never_needs_web`; `test_report_and_adjudicate_at_J_denied_timeout_allowed` |
| AWAITING_REFUND accepts only timeout at/after J, holds full bonds before J, preserves original vector | `test_earlier_uncertainty_blocks_later_fault_until_deadline`; `test_awaiting_refund_accepts_only_timeout_and_preserves_vector` |
| All five writes reject all four terminal states; read-only audit remains available | `test_all_terminal_writes_revert_and_views_survive` (20 combinations) |
| Section 5: record exactly once, never replace log URLs/digests, accept independent submission order | `test_operator_authorization_duplicate_and_independent_recording_order`; `test_record_digest_validation_case_and_immutable_bytes` |
| Unknown slots, invalid digest format rejected; accepted digest normalized to lowercase | `test_unknown_step_and_oversized_or_blank_report_revert`; `test_record_digest_validation_case_and_immutable_bytes` |
| Public HTTPS URL admission rejects HTTP, localhost/IP literals, credentials/fragments/local hostnames | `test_recording_rejects_nonpublic_or_ambiguous_urls` |
| Sole report bound to committed final output URL when present; absent final record still reportable | `test_report_frozen_description_not_in_semantic_prompt`; `test_missing_record_is_that_operators_violation[C]`; `test_pipeline_minimum_and_maximum_step_counts` |
| Approved amendment: every configured operator is excluded as claimant and rejection leaves state unchanged | `test_configured_operator_cannot_claim` (all three configured addresses) |
| Claimant is actual sender; independent address succeeds; description is bounded and never a semantic instruction | `test_configured_operator_cannot_claim`; `test_report_frozen_description_not_in_semantic_prompt`; `test_unknown_step_and_oversized_or_blank_report_revert` |
| Section 6: collect every configured step and attempt both logs even after an early decisive violation | `test_later_unavailable_does_not_hide_earlier_violation_and_all_logs_fetched`; `test_pipeline_minimum_and_maximum_step_counts` |
| Missing record yields deterministic VIOLATION/MISSING_RECORD and retains explicit missing observations | `test_missing_record_is_that_operators_violation` (A, B and C) |
| Eligible changed body yields deterministic TAMPERED/VIOLATION, not a model excuse | `test_changed_eligible_log_is_tampered_and_blamed` (input and output) |
| Tampered side outranks unavailable other side within a step; retain both observations | `test_tampered_side_outranks_other_unavailable_side` |
| Only exactly HTTP 200 accepted; empty, whitespace, oversized and invalid UTF-8 unavailable | `test_ineligible_evidence_is_unavailable_not_a_tamper` (10 eligibility cases) |
| Transport failure/non-byte response unavailable with stable observation fields | `test_transport_and_wrong_body_type_unavailable` |
| Complete 15,000-byte UTF-8 body accepted; 15,001 unavailable; hash exact bytes without normalization/truncation | `test_exact_byte_boundary_and_complete_text_no_normalization`; `test_ineligible_evidence_is_unavailable_not_a_tamper[15001-bytes]` |
| Local prompts include only frozen charter/local duty/full received input and output; no payer/claimant allegation | `test_exact_byte_boundary_and_complete_text_no_normalization`; `test_report_frozen_description_not_in_semantic_prompt`; reviewed `_assess` prompt construction |
| Local FAITHFUL/VIOLATION/UNCLEAR labels accepted; malformed schema/extra keys/invocation failure rejected rather than becoming UNCLEAR | `test_settlement_allocates_only_earliest_bond`; `test_earlier_uncertainty_blocks_later_fault_until_deadline`; `test_malformed_model_cannot_become_unclear_or_mutate_state`; `test_model_invocation_failure_and_consensus_rejection_rollback` |
| Section 7: snapshot binds schema, contract, charter/order/bonds/deadlines, recordings, report and ledger | `test_snapshot_binds_contract_config_records_report_and_ledger` |
| Exact result schema/types/order, no extra fields, no missing steps, commitment/operator/URL bindings | `test_whole_candidate_forgery_rejected_even_same_payee` (14 mutations) |
| Independently rerun web/model work, compare whole result even when attribution is unchanged | `test_later_unavailable_does_not_hide_earlier_violation_and_all_logs_fetched`; `test_whole_candidate_forgery_rejected_even_same_payee`; `test_independent_validator_rejects_changed_fetch_and_errors` |
| Availability reason/status/body length/digests consensus-bound; 404 vs 503 disagreement cannot be ignored | `test_unavailable_consensus_binds_every_observation_even_if_outcome_same`; `test_whole_candidate_forgery_rejected_even_same_payee` |
| Non-return leader/error and malformed candidate rejected; no accounting/storage writes in callbacks | `test_independent_validator_rejects_changed_fetch_and_errors`; `test_model_invocation_failure_and_consensus_rejection_rollback`; callback source review and post-validator state assertions |
| Section 8 / acceptance: B violates, C faithfully propagates -> only B slashed, C refunded | `test_settlement_allocates_only_earliest_bond[B-fault-C-faithful]` |
| A violates -> only A slashed, B and C refunded | `test_settlement_allocates_only_earliest_bond[A-fault]` |
| No violation -> NO_PIPELINE_FAULT and all refunded immediately | `test_settlement_allocates_only_earliest_bond[no-fault]` |
| First violation determines allocation; multiple downstream violations still cause only one slash | `test_settlement_allocates_only_earliest_bond[multiple-faults-only-B-pays]`; `test_pipeline_minimum_and_maximum_step_counts` |
| Earlier UNCLEAR/UNAVAILABLE prevents later blame; no slash and refund at J | `test_earlier_uncertainty_blocks_later_fault_until_deadline` |
| Missing/tampered later slot does not defeat earlier uncertainty barrier | `test_earlier_unknown_also_blocks_evidence_misconduct` |
| Later uncertainty/unavailability cannot defeat an established earlier violation | `test_settlement_allocates_only_earliest_bond[A-fault-before-unclear]`; `test_later_unavailable_does_not_hide_earlier_violation_and_all_logs_fetched` |
| Receipt binds config, complete assessment, allocation ledger and timestamp; not rewritten by replay | `test_receipt_binds_accounting_assessment_and_config_once` |
| Section 9: deposited = available + locked + slashed + refunded after every action, per owner and globally | `Pipeline.check` in every successful-write helper and every rejected-call helper; all lifecycle tests |
| Refunds and claimant credits are projections, never double-counted; full bond only; all other bonds refunded | `test_settlement_allocates_only_earliest_bond`; `test_partial_deposits_activate_atomically_and_configuration_stays_frozen`; `test_deposit_cap_and_unfunded_cancellation` |
| Terminal balances have zero available/locked; nonterminal activated bonds stay locked; exactly-once latches | `Pipeline.check`; `test_earlier_uncertainty_blocks_later_fault_until_deadline`; `test_all_terminal_writes_revert_and_views_survive` |
| Section 10: availability escape hatch, log authenticity/continuity, Sybil claimant and liveness limitations remain documented | `test_earlier_uncertainty_blocks_later_fault_until_deadline` proves availability behavior; other limits are explicit non-guarantees in DESIGN and README, not properties mocked tests can prove away |
| Section 11: source-backed distinction from the four existing mechanisms | Retained Phase 1 design source table, function/line comparisons and source hashes; no runtime novelty test claimed |
| Section 12 delivery: lint, exact runner, all tests, LF and local commit, no push | `tools/verify_local.py`, this handoff's source commit/blob, Git status/remote checks; exact results above |
| Section 13: deployment/finality, fixture hosting, live expected failures and Portal evidence | Deferred by latest Phase 2-only scope; no live coverage or release claim |

The approved design uses semantic judgment on actual inputs. These local tests deliberately supply mocked labels to test the contract's treatment of those labels; they do not demonstrate that live LLMs will classify the proposed email incidents correctly. That remains a review/Phase 3 requirement.

## Implementation choices, uncertainties and deviations

1. **State representation.** The bounded (maximum five-step) configuration, ledger and records are canonically JSON-encoded in one declared GenLayer `str` storage field. This is an implementation simplification of the design's structured storage: it avoids unbounded collections, and integer amounts are explicitly capped at `10**18` per operator. The linter and direct SDK validate it. No money uses floating point. The fixed JSON schema is not an upgrade mechanism.
2. **URL restriction.** Admission conservatively rejects ports and query strings in addition to the design's required credential/fragment/scheme/local-literal exclusions. This is a narrower URL syntax than arbitrary public HTTPS; commit-pinned raw GitHub fixture paths remain supported. It is the only additional input restriction relative to the stated minimum design rules. No redirect or DNS-publicness guarantee is claimed. A public-looking hostname can resolve privately; the approved design requires hosted-runner policy/redirect review before live use, with evidence-host restriction or an explicit limitation if necessary.
3. **Unavailable versus tampered precedence.** A response must first be complete, nonempty, at most 15,000 bytes and strictly usable UTF-8 text. Only eligible bodies are hashed for the integrity verdict. Thus invalid UTF-8/oversized/empty content is UNAVAILABLE even if it would also differ from a committed digest. This is the design's explicit rule. A verified tampered side still wins over an unavailable other side within the same step. Deleting a log can block attribution; the contract does not claim that every kind of withholding is slashable.
4. **Evidence truth and adjacent handoffs.** No signature verification or predecessor digest equality is added. The contract judges each operator's committed claim about its input/output, not authenticated execution. This is the approved design, not a repaired chain-of-custody claim.
5. **Local compatibility shim.** The existing v2 Windows/legacy-SDK test shim is reused only under `tests/`. It patches direct-loader/message behavior and exposes captured validator callbacks. It is not part of deployed contract code. Direct-mode/hosted runner behavior and network finality must remain distinct in later reporting.
6. **Model and network uncertainty.** Actual model agreement, runner web-fetch/redirect behavior and resource limits, deployed-source byte equality, account availability and finality were not tested because this phase prohibits live work. Malformed model output causes a rejected candidate, and deterministic timeout refunds protect liveness without proving no fault. No fallback model or weakened comparison was added.
7. **Scope/deviation summary.** The only approved policy change is configured-operator claimant exclusion. Funding, earliest-fault ordering, exact whole-result comparison, unavailable-log barrier and deadline refund follow the design. The JSON representation and conservative URL syntax are disclosed above. There is no implementation override, second incident, automatic deadline execution, post-terminal withdrawal or additional payout path. Phase 3 is intentionally deferred under the user's latest instruction.

## Review handoff

Review the source commit and `docs/DESIGN.md` before any Phase 3 action, concentrating on the storage representation, conservative evidence admission, actual hosted runner API, the full result equality boundary and prompt/duty allocation. The proposed separate public fixture repository is only a plan at this point; neither that repository nor a contract remote was created by this Phase 2 delivery. The contract repository must remain private if created later. Never submit to the Portal on the owner's behalf.

PHASE 2 COMPLETE. Switch to the stronger model for review and Phase 3.
