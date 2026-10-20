# Liability Cascade

Validators judge each ordered pipeline step against its own received input and frozen duty. Deterministic code selects the earliest proven violation, slashes only that operator's full synthetic bond to the nonoperator claimant, and refunds every other operator. An earlier unclear or unavailable step blocks attribution and leads to deadline refunds. The complete ordered assessment, including every evidence observation and local verdict, is compared exactly.

## Verified release — 2026-10-20

| Gate | Result | Evidence |
|---|---|---|
| Design and scoped distinctiveness | PASS | [DESIGN](docs/DESIGN.md), section 11: source-backed comparison with Faultline, SlashCourt, Evidence Retraction Registry, and Delegated Task Handoff |
| Code review, adversarial tests and lint | PASS | [REVIEW](docs/REVIEW.md); 193 tests, 0 failures/errors/skips; 3 AST checks and SDK validation passed |
| StudioNet source, execution, consensus and accounting | PASS | [Full manifest](deployments/studionet-release-2026-10-20.json) and [independent release audit](deployments/release-audit-2026-10-20.json): 26 FINALIZED transactions, 18 successful executions, 8 expected rollbacks; 28 accounting/state readbacks |

The contract repository is **PRIVATE**. No Portal submission was made. Public evidence is fixture text only in [genlayer-demo-evidence](https://github.com/JWattjr/genlayer-demo-evidence/tree/61b7d56d8147e0f97d89b4e8f4b424141ebaff3c/liability-cascade).

| Incident | Contract address | Stored A/B/C verdicts | Deterministic allocation | Finalized adjudication |
|---|---|---|---|---|
| incident-b | `0x9177a491ac18427e94ecF5FDB841f172Ed6728a7` | FAITHFUL, VIOLATION, FAITHFUL | B only: 100 slashed; 200 refunded | [0x5cfa5a00f6e7718749763ad326e314a79df5175fbb8304efa59550d69c53610c](https://explorer-studio.genlayer.com/tx/0x5cfa5a00f6e7718749763ad326e314a79df5175fbb8304efa59550d69c53610c) |
| incident-a | `0xFee3185d163EF779A9e656DA55399aa341Da7fcF` | VIOLATION, FAITHFUL, FAITHFUL | A only: 100 slashed; 200 refunded | [0x4991aa213147a803c956e1e2315c2857fa6fd4d6d5368d6527b39b17df8bc2fa](https://explorer-studio.genlayer.com/tx/0x4991aa213147a803c956e1e2315c2857fa6fd4d6d5368d6527b39b17df8bc2fa) |

Every configured operator deposited 100 synthetic units from its own sender address. The final deposit activated all bonds atomically. Both incidents rejected a nonoperator recording, a replacement recording, a configured operator's report, and post-settlement adjudication replay. Each rejected call preserved stored state and accounting. Every transaction's actual observed ACCEPTED/FINALIZED history, execution payload and validator votes is retained separately; lifecycle success is not used as a substitute for contract execution success.

## Source and fixture provenance

- Reviewed commit: `2619c4e7b2963117571f383ee8ef1dff9b2d7c07`. The review added 75 adversarial regression cases and found no production-code defect in the reviewed consensus and settlement paths.
- Final regression-test blob: `20bc8d6245a02027603148f1244226600a191c9e`, including the accepted-original-snapshot positive control before each foreign replay rejection. The final verification remains 193 passing cases.
- Deployment-source commit: `da39762abefd3027ab72d47821c06313db1e1993`; contract Git blob `53ff0f7eb7b7be57115886476c55e282b8ab3492`; SHA-256 `b5118d6cd32ef3a642795b4e046fa0bdc13b9f60960fd900833d7e80962dff40`. Both deployed sources match this blob byte-for-byte, including the final LF.
- Runner: `py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6`. The newer-runner notice is informational; the approved pin was retained.
- Public fixture commit: `61b7d56d8147e0f97d89b4e8f4b424141ebaff3c`. `curl` fetched all 12 exact commit-pinned raw URLs with HTTP 200 and no followed redirects. Total body size: 1,404 bytes. Digests are over the exact served LF UTF-8 bytes; [measurement manifest](fixtures/evidence-manifest.json).
- Final publication adds the final replay-test refinement, documentation and receipts after the deployment-source commit. The single private push must contain that ancestor and the identical contract blob. The pushed release HEAD is reported separately; it is not falsely embedded in a commit that would have to contain its own SHA. `tools/verify_remote.py` verifies the private remote HEAD, ancestry and exact source bytes and saves an ignored local proof in `artifacts/remote-publication-verification.json` after the push.

## Demonstration policy and actors

The charter explicitly assigns source-email redaction to A. B uppercases names/regions and preserves contact values exactly as received, never restoring a value absent from its input. C reproduces received CSV bytes and has no independent filtering duty. Thus B/C can faithfully propagate inherited bad data in the A-fault incident. In the B-fault incident A redacts correctly, B restores an email, and C faithfully copies B's output. These are fictional example.org contacts, not real personal data.

| Role | Existing test-account alias | Public address |
|---|---|---|
| A | `moment-grid-studionet` | `0xdB433ff614bDD1ecE21Aa97221C3E0a7ecf79c92` |
| B | `portal-five-release` | `0x2C8EB5dB1105A85BE66BadafeD88D10cF393CDD8` |
| C | `portal-five-release-new` | `0x0839A6DDCeC7aA5E6028490266D6D3EFabE316B5` |
| claimant | `footnote-independent-studionet` | `0xbc1A363B1427531fCb05D03dDF4d34E729011186` |

No keys or credentials are included. StudioNet is gasless; synthetic `deposit(100)` is a required contract participation action, not GEN funding.

## Local verification and interface

Use the existing pinned environment, without upgrades:

```powershell
& 'C:\Users\User\Desktop\Genlayer apps\intelligent-contracts-v2\.venv\Scripts\python.exe' tools/verify_local.py
& 'C:\Users\User\Desktop\Genlayer apps\intelligent-contracts-v2\.venv\Scripts\python.exe' tools/audit_release.py
```

Public writes: `deposit(amount_units)`, `record_step(step_id,input_url,output_url,input_digest,output_digest)`, `report_failure(final_output_url,description)`, `adjudicate()`, `settle_deadline()`. Views: `get_state()` and `get_accounting()`. All writes are nonpayable and reject terminal state. Exact typed signatures and the historical Phase 2 coverage map are in [PHASE2_HANDOFF](docs/PHASE2_HANDOFF.md). [TEST_MATRIX](docs/TEST_MATRIX.md) maps this release's local and live evidence.

The direct-mode Windows compatibility shim uses SDK v0.6.0-rc5 and explicit captured validator callbacks. Live execution uses genlayer-py 0.19.0rc2 with the scoped, copied license-bundle-clearinghouse calldata adapter for this exact StudioNet runner. It does not use the incompatible unadapted encoding path. The live runner saves each returned hash before polling and refuses an uncertain submission or a recorded unexpected judgment; never delete the manifest to retry a judgment.

## Limits

Bonds and payouts are synthetic units with no token custody. Fixture logs demonstrate classification; hashes prove byte consistency, not authentic execution or adjacent handoff continuity. Unavailable evidence before the first proven violation can block attribution; a permissionless transaction at/after the adjudication deadline refunds instead of proving innocence. Operator-address exclusion does not prevent an affiliated unconfigured claimant. URL syntax admission does not prove DNS/redirect publicness; this release uses only the measured commit-pinned raw GitHub URLs and claims no general network sandbox guarantee. Exact comparison can fail consensus when availability or semantic labels differ. The distinction from existing projects is scoped to the inspected local source snapshots, not global novelty.

See [evidence inventory](docs/EVIDENCE.md) and [owner-only submission draft](SUBMISSION_DRAFT.md). Keep this repository private; no visibility conversion or Portal action is part of this release.
