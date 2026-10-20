# LIABILITY CASCADE - Phase 1 design

Date: 2026-10-20 (Africa/Lagos). Status: approved design with the Phase 2 operator-claimant amendment. Phase 2 implementation and verification are documented in `PHASE2_HANDOFF.md`; the reviewed live release is documented in deployments/studionet-release-2026-10-20.json.

## 1. Scope and decision

One deployment represents one ordered pipeline and, at most, one reported incident. Validators assess whether each operator faithfully performed its own duty **given the input that step received**. Deterministic code scans the complete assessment in pipeline order, selects the first provable violation, and slashes only that operator's entire frozen bond to the first eligible claimant. No configured operator may be that claimant. Every other operator receives its bond back. An earlier unresolved step prevents attribution to a later operator.

**Distinctiveness gate: PASS, scoped to the local source snapshots listed in section 11.** Faultline already has a charter, a three-agent pipeline, immutable hash-bearing handoffs, comparative validators, tamper handling, and deterministic synthetic bond settlement. Those are shared features, not novelty claims. The material change is replacing model-assigned PRIMARY/CONTRIBUTING responsibility with an ordered vector of input-conditioned local verdicts and a deterministic first-violation scan with an uncertainty barrier. SlashCourt already separates subjective judgment from penalty arithmetic, but settles a single operator's commitment rather than allocating responsibility across a pipeline. Section 11 gives source-level evidence and counterexamples.

This is a source-based differentiation finding, not a claim of global novelty. If Phase 2 merely reuses Faultline's role assignment or compares only its eventual payee, the distinction would collapse and implementation must stop.

Phase 2 was delivered and stopped at its local handoff. The owner subsequently authorized a stronger-model code review and Phase 3 end to end on 2026-10-20, with no further approval stop. `docs/REVIEW.md` records the review and adversarial re-verification. Phase 3 may publish fixture text in the separate approved public evidence repository and deploy on StudioNet; the contract repository must stay private, its single push is reserved for the end, keys must never be printed, and the Portal must never be submitted. Stop on an unexpected live judgment or a true blocker.

## 2. Authority boundary and frozen configuration

GenLayer owns operator authorization, commitments, deadlines, the complete consensus assessment, deterministic attribution, and synthetic accounting. External hosts supply bytes, not authoritative verdicts. A client can prepare hashes and display provisional outcomes but cannot supply an authoritative judgment or payout.

The constructor freezes these inputs without later setters:

| Field | Proposed validation |
|---|---|
| `pipeline_id` | 1-64 ASCII letters/digits, `_` or `-`; local deployment identifier, not a globally enforced unique name |
| `charter` | One nonblank natural-language charter, at most 4,000 UTF-8 bytes |
| Ordered steps | 2-5 items, each with a unique bounded `step_id`, a distinct nonzero operator address, and a nonblank duty of at most 2,000 UTF-8 bytes |
| Operator bond | One positive integer of at most `10**18` synthetic units per distinct operator; reject booleans and noninteger amounts |
| `recording_deadline` | Future Unix UTC seconds |
| `adjudication_deadline` | Unix UTC seconds strictly greater than `recording_deadline` |

The order is constructor order and never submission order. An operator cannot own two slots in this version, making "one slashed operator" and "one slashed bond" unambiguous. The contract uses canonical address values for authorization; it never trusts an address embedded in a log.

The implementation must begin with exactly:

```python
# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
```

Storage will use declared GenLayer storage fields, `TreeMap`/`DynArray` where appropriate, and bounded integer accounting. Temporary Python dictionaries/lists may build canonical snapshots; they are not substituted for storage types. No native token deposits or transfers are accepted.

### Funding choice needed to make the deposit ledger concrete

The constructor freezes obligations but does not invent funded balances or debit operators without an operator action. The deployment starts in `FUNDING` with zero deposits. Each named operator may call `deposit(amount_units)` before the recording deadline, crediting **synthetic demo units** only to that sender's deposit ledger. Deposits are positive, bounded, and capped at that operator's frozen bond. The caller explicitly opts into this configured demo pipeline; third parties cannot fund a slot on its behalf.

When all operators have deposited exactly their required bonds, that final deposit atomically moves every operator's available deposit into its locked bond and enters `RECORDING`. No additional deposits or withdrawals are allowed. Failure to finish funding by the recording deadline permits cancellation and refund of all deposits, with no incident or fault finding. Missing-record penalties apply only after successful activation. This funding precondition avoids slashing an operator who never joined; it is an explicit design completion of the brief's unspecified deposit lifecycle.

## 3. Participants and callable actions

| Participant | Permitted actions | Authority limits |
|---|---|---|
| Deployer | Freeze the constructor configuration | No later override, admin slash, deadline extension, charter edit, or incident reset |
| Named operator | Deposit its own synthetic bond during funding; record its own step once during recording | Cannot record another slot, replace a log URL/digest, recover a locked bond early, or amend its duty |
| Any account except configured operators / prospective claimant | Open the first failure report after recording closes and before adjudication closes | Reporter identity is the transaction sender; reject every configured operator address; only one incident and claimant are stored |
| Any account / adjudicator | Call `adjudicate()` once successfully while a report is open | No ability to supply verdicts, override evidence, or choose a payer |
| Any account / timeout caller | Call `settle_deadline()` after the appropriate deadline | Deterministic refund only; cannot fabricate a completed assessment or slash on timeout |
| Validators | Independently fetch logs and assess each eligible step inside the nondeterministic execution | Must agree on the whole canonical result; model output contains no payer or amount |
| Read-only observer | Read configuration, records, report, assessment, settlement and accounting | Views remain available after terminal settlement |

"No actions after terminal state" means every public **write** reverts. Views remain available so the terminal record can be audited. Refund and claimant credits are written atomically with settlement, so there is no post-terminal withdrawal action.

## 4. State machine and exact time boundaries

Let `t` be the deterministic transaction timestamp, `R` the recording deadline and `J` the adjudication deadline. Wall-clock time in the client, the evidence server's clock, and an LLM's time claims have no authority.

```text
constructor -> FUNDING
  final required deposit, t < R -> RECORDING (all bonds locked)
  settle_deadline, t >= R -> CANCELLED_UNFUNDED (refund; terminal)

RECORDING
  record_step, t < R -> RECORDING (one slot becomes immutable)
  report_failure, R <= t < J -> REPORTED
  settle_deadline, t >= J -> SETTLED_UNATTRIBUTABLE (NO_REPORT; terminal)

REPORTED
  successful adjudicate, R <= t < J:
    first provable violation -> SETTLED_FAULT (terminal)
    every step faithful -> SETTLED_NO_PIPELINE_FAULT (terminal)
    uncertainty before any violation -> AWAITING_REFUND
  settle_deadline, t >= J -> SETTLED_UNATTRIBUTABLE (NO_ASSESSMENT; terminal)

AWAITING_REFUND (assessment already frozen; outcome UNATTRIBUTABLE)
  settle_deadline, t >= J -> SETTLED_UNATTRIBUTABLE (terminal)
```

Recording is logically closed at `t == R` even if the stored state still reads `RECORDING`. It never closes early when the last slot records. Reporting and adjudication are disallowed at `t == J`. Time does not execute a transaction automatically: "refund at the deadline" means the first successful permissionless timeout call at or after it. A view should expose the effective time window as well as stored state.

`AWAITING_REFUND` is deliberately nonterminal. It exposes `outcome = UNATTRIBUTABLE`, `settled = false`, and the frozen assessment, while all bonds remain locked until `J`. It accepts no second report, recording, deposit, or adjudication. This reconciles an immediate unattributable finding with the required deadline-delayed refund.

An adjudication transaction that reverts or fails consensus commits no state, no assessment, and no accounting change. It does not consume the successful-adjudication latch. A completed assessment consumes that latch even if its result is unattributable. A second successful-path call always reverts. Operationally, an unexpected live judgment must be reported rather than retried; a new caller does not reopen a completed judgment.

Timeout settlement performs no web fetch and no LLM call. It cannot be blocked by an evidence host or a failure of model consensus. Timeout and adjudication are serialized by contract state and the disjoint time boundaries; whichever valid terminal transition commits makes later writes revert.

## 5. Recording and reporting

### `record_step(step_id, input_url, output_url, input_digest, output_digest)`

Require activated `RECORDING`, `t < R`, a known step, the sender equal to its frozen operator, and no previous record for that step. Validate both URLs as bounded public HTTPS references and each digest as exactly 64 hexadecimal SHA-256 characters, stored lowercase. Store both URLs, both digests, operator, step index and transaction timestamp once.

Each step may record independently and in any transaction order. A missing upstream record must not prevent a downstream operator from preserving its own evidence. There is no delete, replacement, update, or second recording window. No evidence is fetched at recording time; the commitment is to the eventual adjudication bytes, not a claim that the server was checked on submission.

URLs are at most 2,048 characters. Reject credentials, fragments, non-HTTPS schemes, localhost, local/private IP literals, and malformed authorities. Prefer commit-pinned `raw.githubusercontent.com` paths for the live fixture. A public-looking DNS name alone cannot prove its resolved address is public; the actual runner's network policy and redirect behavior must be checked before live use. If the runner cannot enforce the intended public-HTTPS policy through redirects, Phase 2 must restrict evidence to approved raw GitHub commit URLs or report the limitation before Phase 3.

Digests cover the exact complete response-body bytes exposed by the web API. Do not trim, normalize newlines, replace decoding errors, parse/re-serialize JSON, strip HTML, or hash a truncated prefix. Authors must calculate digests from the exact LF fixture bytes that will be served.

### `report_failure(final_output_url, description)`

Require an activated pipeline, no previous report or assessment, and `R <= t < J`. Reject the sender if its canonical address equals **any configured operator**, including an operator whose own record is missing. Any other account may call. Freeze that sender as `claimant`, a valid bounded HTTPS `final_output_url`, a nonblank description of at most 2,000 UTF-8 bytes, and the report timestamp. An operator rejection must leave the report, phase and accounting unchanged.

If the final step recorded, require `final_output_url` to equal its committed output URL. That committed log supplies the final evidence; there is no second uncommitted fetch that can override it. If the final step never recorded, retain the report URL as a contextual reference only; its absent record is classified by the deterministic missing-record rule. The description is an allegation, not a verdict, and is not included in the step-classification prompt. A report need not prove final failure before the pipeline is assessed: if every local step was faithful, the result is `NO_PIPELINE_FAULT`.

The first valid nonoperator reporter captures the claimant role and any award. Front-running and use of unconfigured affiliated accounts remain possible, as described in section 10. There is no report replacement or claimant reassignment.

## 6. Evidence acquisition and local verdicts

Adjudication produces one record for **every** configured step in frozen order. It attempts both committed log fetches for every recorded step, even if an earlier step already determines the eventual outcome. Missing slots have explicit missing observations; they are never silently omitted. The complete result is bounded by five steps and ten log bodies, each at most 15,000 bytes.

For each committed URL, the independently running validator uses the following eligibility order:

1. A transport failure or an HTTP status other than exactly 200 is `UNAVAILABLE`. This includes 201, 204, 206, redirects returned as such, 404, 429 and 5xx. A partial body is not complete evidence.
2. A non-byte body, an empty body, or a body over 15,000 bytes is `UNAVAILABLE`. Never judge a size-limited prefix. Decode the eligible body strictly as UTF-8; invalid UTF-8 or whitespace-only text is also `UNAVAILABLE`.
3. For an eligible complete body, calculate SHA-256 over the original bytes. A digest different from the commitment is `TAMPERED`. A matching digest is `AVAILABLE` and eligible for semantic judgment.

This order explicitly treats invalid UTF-8, empty and oversized evidence as unavailable, as required by the test brief; those bodies cannot become acceptable text through replacement decoding. Integrity comparison applies to eligible complete log bodies. A change to different eligible text is tampering. An operator can still defeat attribution by making evidence unavailable: the specified fail-closed policy does not equate all availability failures with misconduct.

Keep an observation for each side with exact fields:

```text
url, committed_digest, status, http_status, reason_code,
byte_length, observed_digest
```

`status` is `AVAILABLE`, `TAMPERED`, `UNAVAILABLE` or `NOT_RECORDED`. Missing fields use a fixed sentinel (`null` for unavailable measurements; empty string for absent URL/commitment), not invented bytes or digests. `http_status` is an integer when a response was received, otherwise null. `byte_length` is available for a returned byte body; `observed_digest` is populated for eligible bodies on which the integrity check was performed, otherwise null. Use a closed reason-code set such as `OK`, `NOT_RECORDED`, `TRANSPORT`, `HTTP_STATUS`, `BODY_TYPE`, `EMPTY`, `OVERSIZED`, `INVALID_UTF8`, `EMPTY_TEXT`, `DIGEST_MISMATCH`. Exclude exception messages, response timing, variable headers and server dates.

The step record separates facts from judgment:

| Condition | Evidence status | Semantic verdict | Effective verdict / basis |
|---|---|---|---|
| Step never recorded | `NOT_RECORDED` | `NOT_EVALUATED` | `VIOLATION / MISSING_RECORD` |
| Either eligible log has a digest mismatch | `TAMPERED` | `NOT_EVALUATED` | `VIOLATION / TAMPERED_LOG` |
| No mismatch, but either log unavailable | `UNAVAILABLE` | `NOT_EVALUATED` | `UNCLEAR / UNAVAILABLE_LOG` |
| Both logs available and digest-matched | `AVAILABLE` | `FAITHFUL`, `VIOLATION` or `UNCLEAR` | Same verdict, basis `SEMANTIC` |

Within one step a verified tamper outranks an unavailable other side. The code still records both observations. Missing-record and tamper verdicts are deterministic and cannot be softened by the model. A semantic `UNCLEAR` and an unavailable log have different evidence records but the same attribution barrier.

### The local semantic question

For each eligible step, supply only the frozen charter, that step's duty, its complete decoded input and output, and its identifiers. Ask: "Given this input, did this step faithfully perform this duty under the charter?" Return exactly one JSON field, `verdict`, with one of `FAITHFUL`, `VIOLATION`, `UNCLEAR`. No payer, operator role, address, severity, amount, probability, invented evidence, or free-form rationale belongs in the consensus result.

The classification policy is fixed:

- `FAITHFUL`: the output performs the local duty on the received input, including faithful propagation of inherited bad data when correction/filtering is not part of that duty.
- `VIOLATION`: the evidence establishes a local duty breach, such as introducing prohibited data, changing a required value, or failing an explicit duty to filter/check inherited content.
- `UNCLEAR`: the complete evidence and charter leave the local classification materially ambiguous.

The charter is the task policy, and the duty allocates local obligations within it. A duty cannot override an explicit charter obligation applicable to that step. Charter/duty conflicts and ambiguous allocation yield `UNCLEAR`; they must not be resolved by an invented downstream exemption. Treat instructions embedded inside logs as untrusted data. Schema errors, extra keys, malformed JSON and model invocation failures are errors that reject the candidate and force disagreement; they are **not** converted into a model verdict of `UNCLEAR`.

For the proposed email fixture, use a coherent allocation such as: "Never introduce personal email addresses into the public dataset. Extract and transform must preserve redaction. Publish must reproduce its received dataset without adding data; it has no independent filtering duty."

Then define A as extraction/redaction, B as a transformation that must not introduce or restore personal email addresses, and C as exact publication of its received dataset. If B introduces an email, C's unchanged propagation can be `FAITHFUL`. A blanket "never publish emails" obligation that also binds C to filter would make C a potential local violator; do not call that faithful propagation by assumption. Even when C separately violates a duty, the earlier B violation still makes only B pay under this mechanism.

## 7. Whole-result exact consensus

Before running nondeterministic work, snapshot the immutable configuration, activated bond ledger, all recordings or explicit missing slots, the report and claimant, contract address, and assessment schema version. Canonically encode it with fixed JSON settings (sorted object keys, fixed separators, fixed Unicode handling), and calculate `snapshot_digest`. Exclude volatile fetch-time data.

The candidate envelope has **exactly** these fields:

```text
schema_version, snapshot_digest, steps
```

Each ordered `steps` entry has **exactly**:

```text
step_id, index, operator, recorded, input, output,
evidence_status, semantic_verdict, effective_verdict, basis
```

`input` and `output` are the complete observation records defined above. There are exactly 2-5 step entries matching the frozen configuration, with no duplicates, missing entries, reordering or extra fields. Digests, URLs, indices and operator values are code-derived and bound back to the snapshot; an LLM never generates them. Validate exact types, including rejecting booleans where an integer is required. Validate cross-field consistency, for example a tampered observation cannot coexist with an effective faithful verdict.

Use a custom comparative leader/validator function with the pinned runner's supported nondeterministic primitive. A validator independently fetches **all** recordings and reruns every eligible local classification. It then checks the leader envelope's exact schema and state binding, and compares the **entire canonical candidate** against its independently generated candidate. There is no tolerated difference in any included field: per-step verdicts, committed and observed digests, byte lengths, availability, HTTP status, reason codes and snapshot binding all match exactly. The ordered arrays remain ordered.

Only return success when the leader is a normal return and the whole result is equal. Leader errors, malformed results, and validator-side model failures reject the candidate. A 404 observed by one validator and a transport failure observed by another can therefore fail consensus even though both would prevent slashing. That is an accepted liveness tradeoff, resolved financially by the deterministic deadline refund rather than by weakening comparison.

After consensus, validate the envelope again in deterministic execution, store it once, and compute attribution from its effective verdicts. The envelope contains no attribution field. Thus a forged leader with the same ultimate payer but a different C verdict, changed digest, missing unavailable observation, or altered status is rejected. No storage or accounting mutation inside a nondeterministic callback is permitted.

## 8. Deterministic attribution and settlement

After collecting the entire vector, scan in constructor order:

```text
for step in ordered_steps:
    if step.effective_verdict == VIOLATION:
        outcome = PIPELINE_FAULT
        liable_step = step.step_id
        slash its entire frozen bond to claimant
        refund every other operator
        stop the scan
    if step.effective_verdict == UNCLEAR:
        outcome = UNATTRIBUTABLE
        liable_step = null
        retain all bonds until J
        enter AWAITING_REFUND
        stop the scan

if the scan finishes:
    outcome = NO_PIPELINE_FAULT
    liable_step = null
    refund every operator immediately
```

Missing recordings and verified tampering enter the scan as `VIOLATION`, regardless of any model answer. The first decisive position wins. A later violation cannot overcome an earlier unknown; an unknown after an established earlier violation cannot defeat that attribution. Later assessments remain in the stored consensus record even though they do not change payment.

| A | B | C | Result |
|---|---|---|---|
| FAITHFUL | VIOLATION | FAITHFUL | Only B slashed; A and C refunded |
| VIOLATION | FAITHFUL | FAITHFUL | Only A slashed; B and C refunded |
| FAITHFUL | FAITHFUL | FAITHFUL | NO_PIPELINE_FAULT; all refunded |
| UNCLEAR | VIOLATION | FAITHFUL | UNATTRIBUTABLE; no slash, all refunded at/after J |
| FAITHFUL | UNAVAILABLE | VIOLATION | UNATTRIBUTABLE; same deadline refund |
| VIOLATION | UNAVAILABLE | VIOLATION | Only A slashed |
| NOT_RECORDED | VIOLATION | FAITHFUL | A's missing record is first violation; only A slashed |
| FAITHFUL | TAMPERED | VIOLATION | Only B slashed |
| FAITHFUL | VIOLATION | VIOLATION | Only B slashed; C refunded despite its separate breach |

The last case is intentional: refunding a downstream bond is not necessarily a finding that the downstream step was faithful. It is the contractual allocation rule that caps this incident at one liable operator. "Downstream exoneration" specifically describes the faithful-propagation case; the full stored vector preserves any separate downstream breach.

Settlement writes the outcome, liable index/operator or null, total slashed, per-operator refunds, claimant credit, settlement timestamp, and a receipt digest atomically. It sets `settled = true` exactly once. For an unattributable assessment, deadline settlement preserves its vector and adds refunds without re-adjudicating. For no report or no successful assessment, store the appropriate timeout reason and a null assessment; do not invent per-step verdicts.

## 9. Accounting and invariants

All units are synthetic integers, without economic value. `deposit(amount_units)` is a demo ledger action, not proof of payment or custody. For each deposit owner `i`, maintain four disjoint buckets:

```text
D_i = cumulative synthetic deposits from operator i
A_i = currently available, uncommitted deposit units
L_i = currently locked bond units
S_i = deposit units irreversibly allocated to the claimant by slashing
F_i = deposit units irreversibly returned to operator i as a refund

D_i = A_i + L_i + S_i + F_i
D = sum(D_i) = available + locked + slashed + refunded
```

`S_i` and `F_i` are terminal allocation buckets. Refunds are **not also credited to A_i**. Recipient views expose `refund_credit[operator]` and `award_credit[claimant]` as projections of those allocations; those credits are not added a second time to the conservation equation and cannot be redeposited in this deployment. This avoids mixing cumulative refunds with live available balance.

Transitions are exact integer operations:

| Transition | Ledger movement |
|---|---|
| Funding deposit `x` | `D_i += x; A_i += x`, cap at frozen bond |
| Full activation | For every operator, `A_i -= bond_i; L_i += bond_i` |
| Funding cancellation | For every operator, `F_i += A_i; A_i = 0`; `L_i` was zero |
| Fault settlement | Liable operator: `S_i += L_i; L_i = 0`; every other operator: `F_i += L_i; L_i = 0` |
| No-fault / timeout refund | For every operator, `F_i += L_i; L_i = 0` |
| Unattributable assessment before J | No accounting movement |

For bonds of 100 each, activation yields `D=300, A=0, L=300, S=0, F=0`. A B fault yields `D=300, A=0, L=0, S=100, F=200`, with claimant credit 100, A refund 100 and C refund 100. An unattributable assessment keeps `L=300` until deadline settlement yields `F=300, S=0`.

After every successful public write, assert:

- Global and per-owner conservation; all amounts nonnegative and within bounds.
- At most one operator has a positive slash bucket; slash amount is either zero or exactly that operator's frozen bond.
- Total claimant award equals total slashed; total operator refund credits equal total refunded.
- Activated but unsettled deployments have exactly the configured bonds locked, including `AWAITING_REFUND`.
- Every terminal deployment has zero available and locked units. Funding cancellation returns all actually deposited units, not unfunded obligations.
- Settlement count is at most one; assessment count is at most one; a fault settlement has a claimant and a completed bound assessment.
- Configuration and recordings never change; no write succeeds after terminal settlement.

Rejected calls must leave all storage and accounting unchanged. Compute and validate the complete settlement before applying it, and rely on transaction rollback for any invariant failure; never partially refund within a nondeterministic callback.

## 10. Limits and adversarial cases

**Committed evidence is not authenticated execution.** A digest proves that eligible fetched bytes match an operator's commitment. It does not prove that those logs truthfully describe execution, that the declared input was actually received, or that adjacent steps exchanged matching artifacts. This API does not require a predecessor-output digest equal to the next input digest; different log formats are permitted. Do not claim cryptographically proven end-to-end handoff continuity. Signed receipts or a specified shared artifact format would be a separate extension.

**Availability remains an escape hatch under the requested policy.** Never recording and replacing a log with different eligible text are violations. Removing a committed log, serving unusable bytes, or denying access produces unavailable evidence and can block attribution if it occurs before the first provable violation. The design cannot promise that all withholding is slashable while also honoring the explicit unavailable-log refund rule. This limitation must remain visible in later documentation.

**First-reporter economics are weak.** Every configured operator is prohibited from calling `report_failure`, so its configured address cannot directly receive a claimant award. A front-runner, an unrelated observer or an unconfigured address affiliated with an operator can still become the claimant. Address exclusion does not prove independence or prevent Sybil self-dealing. There is no victim verification, claimant stake, or authenticated harm claim. These are material incentive limits, accepted for the synthetic demonstration rather than hidden behind the payout calculation.

**Local duties need coherent drafting.** An absolute downstream safety obligation can conflict with "faithfully pass through bad input." Validators must evaluate the actual charter and local duty; fixture labels alone cannot define the outcome. Ambiguous policies must produce semantic `UNCLEAR`, not an invented safe harbor.

**Exact agreement can reduce liveness.** Honest validators may disagree about a semantic label or see different server states. Deadline refunds protect locked units, but do not prove absence of pipeline fault. No application-level appeal, remediation attempt, or second incident exists. Network acceptance and finality remain distinct; a provisionally accepted write is not reported as finalized settlement.

**Bounds are evaluation bounds.** Ten 15,000-byte logs mean at most 150,000 eligible log bytes, with each semantic call limited to one input/output pair plus bounded charter/duty. The runner may buffer an oversized response before code checks its size; resource behavior must be checked during implementation. No unbounded evidence crawling, recursive URL fetch, arbitrary log instructions, or summarization-before-hashing is allowed.

## 11. Source-backed distinctiveness review

These comparisons use local files read on 2026-10-20, not names, screenshots, or claims about deployed contracts. Line numbers refer to those file bytes. Source hashes make the review reproducible even if the working copies later change; no repository commit or clean-tree state is asserted for the comparison projects.

Source root: `C:\Users\User\Desktop\Genlayer apps`.

| ID | File below source root | SHA-256 of inspected bytes |
|---|---|---|
| F | `faultline/contracts/faultline.py` | `7403d5ea7c2c493c3dba44de944ed5e81c126f62121d0cb83ed2ec0ed9fe164d` |
| S | `slash-court/contracts/slash_court.py` | `e39b7c25489bc3a54a83f40a6cc3f0219583e89d747274777eb21faaed616bba` |
| V | `slash-court/contracts/operator_bond_vault.py` | `2c51484e09c596c06f0264f98e5beb67e8c075fa02cc7024afb523f77e2554b3` |
| E | `intelligent-contracts-v2/evidence-retraction-registry/contracts/evidence_retraction_registry.py` | `a3243d9dbaa092835eb86844a50300d29be30fb3747caea0421eee37621c4b61` |
| H | `intelligent-contracts-v2/delegated-task-handoff/contracts/delegated_task_handoff.py` | `c81026b0baed9f1c0cc0fca32ad0a839cc75f3fd5f8560b9b918aa2cba267683` |

### Mechanism comparison

| Dimension | Faultline (F) | SlashCourt + vault (S/V) | Evidence Retraction Registry (E) | Delegated Task Handoff (H) | Liability Cascade design |
|---|---|---|---|---|---|
| Subject of judgment | Whole fixed three-agent pipeline, clauses and final artifact | One respondent's frozen service commitment under a versioned rulebook | Whether a publication corrects/retracts a source; whether dependent decisions remain supported | Whether a proposed subtask fits parent scope, preserves constraints and overlaps siblings | Each of 2-5 steps' input-to-output performance under its own duty |
| Responsibility selection | Model assigns exactly one PRIMARY plus optional CONTRIBUTING roles | Model classifies one respondent; code maps classification to fixed penalty | No operator liability selection | No after-the-fact breach attribution | Code selects first effective VIOLATION unless an earlier unknown blocks attribution |
| Multiple local failures | Multiple bonds can be slashed at PRIMARY/CONTRIBUTING rates | One commitment resolved per case; no cross-pipeline ordering | Dependents can all be blocked for reassessment | Parent/child budgets and approvals, no fault slashing | Only one full bond slashed per incident, even when later steps also violate |
| Downstream treatment | CLEAR roles can be returned bonds, but there is no mandatory ordered local-verdict rule | No downstream pipeline in the case | Downstream authorizations disabled until reassessment | Downstream delegation judged before activation | Explicit input-conditioned faithful propagation; only earliest liable bond pays |
| Hash commitments | Operator-authenticated once-per-attempt evidence/artifact hashes plus predecessor-output chain | Hashed evidence manifests submitted during case lifecycle, and a hash-bound commitment | Evidence/snapshot digests bind fetched references and source versions | Snapshot digest binds scope review | Separate immutable input/output log digests before any report; no claimed adjacent-log chain |
| Tampering | Deterministic changed agents become PRIMARY/CONTRIBUTING; tamper proceeds can go to CLEAR agents or be burned | Unavailable or hash-mismatched fetch returns insufficient evidence/no slash | Unavailable evidence can yield UNCERTAIN; source correction blocks dependents | No comparable fetched execution-log tamper branch | Eligible digest mismatch is that step's VIOLATION; first provable step pays claimant |
| Missing record / uncertainty | All three handoffs required to adjudicate; expiry refunds without attribution | Insufficient evidence/external outage map to no slash | UNCERTAIN notices and reassessment stay in registry lifecycle | Rejected/expired proposals release reservations | Missing record is a violation after activation; earlier UNCLEAR/UNAVAILABLE blocks later blame; refund at J |
| Consensus boundary | Basis and tampered sources exact; semantic comparison projects to outcome + agent-role assignments | Binds classification, rules, exemptions, finding references and citations; deterministic amount mapping | Includes input/evidence digests, findings/validity and citations in comparisons | Compares scope decision vector after snapshot validation | Entire exact ordered envelope, including every verdict, digest and availability observation |
| Accounting | Synthetic escrow rewards plus per-role bond rates; no operator-funded deposit action in the inspected charter seal path | Payable native-value deposits, vault exposure, beneficiary/safety-pool split and finality callbacks | No bond deposit/slash accounting | Synthetic delegated budget conservation, recorded spend and refunds | Synthetic operator deposit ledger, all-or-nothing single liable bond, no rewards or safety-pool split |

### Faultline: overlap and the actual change

F `_prompt` (lines 260-306) judges the complete pipeline and asks the model to choose a principal causal failure and downstream contributors, explicitly saying not to infer blame from pipeline position alone. F `_normalize_decision` (309-360) requires one PRIMARY on a breached decision. F `_settle_breached` (833-866) then loops over every agent and applies the configured PRIMARY/CONTRIBUTING rate. Thus code calculates amounts, but the model supplies the liability roles. Merely saying "LLM judgment, deterministic payment" would not distinguish this proposal.

F `submit_handoff` (661-733) already checks the assigned wallet, rejects duplicate handoffs, commits evidence and artifact hashes before adjudication, and enforces predecessor hash continuity. F `_fetch_source` (192-216) hashes the body but evaluates normalized/truncated text (5,500 characters), whereas this design evaluates complete eligible UTF-8 log bodies without text rewriting. Precommitted hashes and downstream CLEAR refunds therefore are overlaps; full separate input/output assessment and the ordered uncertainty barrier are the claimed differences.

F `_tampered_decision` (385-409) already chooses the first changed agent as PRIMARY and later changed agents as CONTRIBUTING. "Earliest tamper" alone would be a superficial difference. This design applies a code-driven order to **all** local semantic and evidence verdicts, never slashes a second bond, and cannot skip an earlier unclear step.

F `_settlement_key` (363-371) compares only outcome and agent-role pairs. The validator (750-762) additionally compares basis and tampered sources, but not the full semantic evidence/verdict vector proposed here. F adjudication requires all three handoffs (736-742); missing-handoff cases instead expire/refund (644-658), unlike this design's deterministic missing-record violation.

Concrete divergence: if B violates and C independently violates, Faultline permits B PRIMARY plus C CONTRIBUTING with both rates positive. Liability Cascade must slash B alone. If A is unclear and B clearly violates, this design must withhold attribution and refund at J; F has no corresponding ordered UNCLEAR verdict schema. Achieving these behaviors requires changing the judgment interface and settlement algorithm, not just renaming fields or configuring a zero contributor rate.

### SlashCourt: shared separation of judgment and arithmetic

S `open_case` (1230-1247) binds one vault commitment and permits its beneficiary to complain. S `_produce_independent_result_with_evidence` (988-1080) classifies PROVABLE_MISCONDUCT, NEGLIGENT_FAILURE, EXTERNAL_OUTAGE or INSUFFICIENT_EVIDENCE. S explicitly excludes penalty fields from model output (1072-1077). S `adjudicate_case` (1415-1470) computes a fixed penalty and queues finalized vault messages; V `apply_resolution` (633-738) checks provenance/replay and splits the penalty between beneficiary and safety pool. This is already genuine judgment-to-settlement separation.

S `_fetch_public_evidence` (609-638) treats non-2xx or hash-mismatch evidence as an unavailable bundle, leading to the insufficient-evidence path (988-998). S manifests are checked/canonicalized at 453-499 and can be appended during the case lifecycle; they are not this design's complete per-step log set frozen before a claimant exists. V `_credit_bond` (400-417) uses payable value, unlike this synthetic ledger. S `_consensus_bound_result` and `_evaluate_with_consensus` (1086-1152) already bind substantive findings and evidence, so evidence-bound validation alone is not new.

The substantive difference is one incident-wide ordered allocation across several operators, with local input-conditioned verdicts and an earlier-unknown barrier. A series of independent SlashCourt cases would not enforce the single-slash cap or automatically refund other pipeline participants when the earliest liable step is selected.

### Evidence Retraction Registry and Delegated Task Handoff

E `_assess_notice` (540-644) compares registered references with a new publication and binds input/evidence digests. `submit_notice` (789-861) versions a corrected or retracted source; `_propagate_block` (646-671) marks descendants BLOCKED_REASSESSMENT and disables authorization. `reassess_decision` (968-1018) evaluates replacement dependencies and creates a new decision version. The overlap is externally fetched evidence and dependency-aware consequences, not bond attribution. This design refunds unaffected/downstream bonds according to the earliest breach rather than invalidating a decision graph; it has no source-version or correction mechanism.

H `_assess_scope` (261-303) reviews containment, constraint preservation and overlap against the specific parent. `_activate_handoff` (318-347) assigns a child budget and owner; `record_spend`, `complete_assignment` and `refund_unspent_budget` (483-541) conserve budget through completion. The overlap is local context, frozen constraints and synthetic accounting. Its model evaluates prospective task authorization, not recorded input/output performance, and the source has no post-incident earliest-violation slash path. A local-context judgment alone is not this proposal's novelty.

## 12. Approved Phase 2 acceptance plan

Implementation uses the pinned existing environment at `C:\Users\User\Desktop\Genlayer apps\intelligent-contracts-v2\.venv`, with LF source and `.gitattributes` containing `* text=auto eol=lf`. Do not replace the venv or silently upgrade the toolchain. The direct-mode and lint skills were inspected for Phase 2.

The approved test matrix includes all requested cases and the state-machine edges introduced here. Executed results are recorded in PHASE2_HANDOFF.md and REVIEW.md:

| Area | Required evidence |
|---|---|
| Basic liability | B violates/C faithfully propagates: only B slashed and C refunded; A violates: only A slashed; all faithful: all refunded |
| Ordering | UNCLEAR before violation yields UNATTRIBUTABLE with zero slash; UNAVAILABLE before violation same; violation before unknown still slashes only that earlier step; multiple violations never slash two |
| Evidence misconduct | A never-recorded slot and an eligible changed-body digest each become that operator's violation, subject to any earlier uncertainty barrier |
| Authorization and immutability | Nonoperator recording, duplicate recording, recording at/after R, second report, charter change attempts and second adjudication revert with unchanged storage |
| Operator-claimant exclusion | Every configured operator calling `report_failure` reverts; an otherwise valid nonoperator report still succeeds; report state and accounting remain unchanged on each rejection |
| Evidence eligibility | Non-200, empty, whitespace-only, oversized and invalid UTF-8 become UNAVAILABLE; 15,000 bytes accepted when valid and matching, 15,001 rejected; no partial text evaluation |
| Intra-step precedence | Tampered side plus unavailable other side yields VIOLATION with both observations preserved |
| Exact consensus | Directly invoke the validator callback with a mocked leader return: same final payer but different per-step verdict, observed/committed digest, availability, reason/status, missing entry, order or snapshot must be rejected |
| Funding | Own-sender bounded deposits, full activation, insufficient funding at R refunds actual deposits without missing-record blame; reject excess/zero/boolean deposit |
| Deadline and liveness | Report at R allowed, record at R denied; report/adjudicate at J denied; timeout at J allowed; no report/no assessment refund; AWAITING_REFUND cannot settle before J and cannot adjudicate again |
| Invariants | Global/per-owner equations and recipient-credit projections after every write; reverts preserve balances; every terminal write rejected; settle count at most one |
| Delivery | Pinned runner header, contract lint passes, LF verified, local commit recorded, no push; then STOP |

Ordinary direct execution alone does not prove validator agreement. Tests of forged leaders must explicitly exercise the actual comparison callback with independent mocked web/model work. Real distributed consensus and deployment status remain Phase 3 evidence, not conclusions drawn from direct tests.

## 13. Later live gate and reporting

When explicitly approved, Phase 3 is StudioNet only and uses GenLayerJS or the known license-bundle-clearinghouse client adapter. Do not use the known-incompatible genlayer-py 0.19.0rc2 encoding path for live calls. The approved key helper may be consumed by a process without printing its output; no credential is read or invoked during Phase 1.

Later live evidence must cover the two separate deployments (B introduces fault, then A introduces fault), pinned raw GitHub log URLs, curl-measured complete body bytes, expected nonoperator and replacement failures, constructor args, deployed/source-blob byte equality, transaction execution/votes, ACCEPTED versus FINALIZED, and state reads after every action. An unexpected judgment stops the run for reporting. Creating a private remote, confirming its deployed source commit, writing the dated release manifest and README/TEST_MATRIX/SUBMISSION_DRAFT, and preparing a Portal note under 1,000 characters all belong to that later gate. Never make the repository public or submit the Portal form; the owner handles any eventual public conversion and submission.

**Phase 3 evidence-publication plan, clarified by the owner.** Public fixture text will live under `liability-cascade/` in `JWattjr/genlayer-demo-evidence`, published before deployment and referenced at its exact commit SHA. That evidence repository may contain fixture text only: no contract code, keys or secrets. The contract repository `JWattjr/liability-cascade` stays private. This resolves the original conflict between private evidence, unauthenticated validator retrieval and a first/only contract-repository push at the end. GitHub documents [private-repository access restrictions](https://docs.github.com/en/repositories/creating-and-managing-repositories/about-repositories#about-repository-visibility) and [authentication for repository content, including raw representations](https://docs.github.com/en/rest/repos/contents#get-repository-content).

The original Phase 2 handoff prohibited repository creation, publication, credentials and deployment during that phase. The subsequent review/Phase 3 instruction now explicitly authorizes those live actions under the constraints above. Never expose repository credentials in on-chain URLs, embed tokens in fixture references, or make the contract repository public. Live execution uses three distinct operator accounts and a fourth nonoperator claimant; only public addresses and aliases are recorded.

Final release gates: design/differentiation PASS, local review/tests/lint PASS (193 tests), live/source/finality PASS. The full release manifest records two byte-matched deployments, 26 FINALIZED transactions, eight expected rollbacks, stored judgments and 28 passing accounting readbacks. See REVIEW.md, TEST_MATRIX.md and EVIDENCE.md. The contract repository remains private; no Portal submission was made.
