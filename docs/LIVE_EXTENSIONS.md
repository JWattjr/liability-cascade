# Additional live incidents 3 and 4

- [0x56e7E3b200bD95ef44cea1a71cc3a626026E103f](https://explorer-studio.genlayer.com/address/0x56e7E3b200bD95ef44cea1a71cc3a626026E103f) — incident-3
- [0x580326cD677EE0a613Aa4efAeb648A3cfa8Ed2A4](https://explorer-studio.genlayer.com/address/0x580326cD677EE0a613Aa4efAeb648A3cfa8Ed2A4) — incident-4

Both deployed from the exact source at `da39762abefd3027ab72d47821c06313db1e1993`, contract blob `53ff0f7eb7b7be57115886476c55e282b8ab3492`, SHA-256 `b5118d6cd32ef3a642795b4e046fa0bdc13b9f60960fd900833d7e80962dff40`. Both on-chain bodies match that blob byte-for-byte. No contract source was changed. The same three operator accounts and distinct fourth-account claimant were used.

## Results and the allocation distinction

Incident 3 stored **A FAITHFUL, B VIOLATION, C VIOLATION**, outcome **PIPELINE_FAULT**, phase **SETTLED_FAULT**. Only B lost its 100-unit bond. A and C each received a 100-unit refund. C's stored semantic/effective VIOLATION remains visible: its refund follows the single-earliest-payer allocation rule and is not a finding that C was faithful. B restored Leah's email; C independently restored Theo's email absent from C's input.

Incident 4 stored **A UNCLEAR/UNAVAILABLE, B VIOLATION, C FAITHFUL**, outcome **UNATTRIBUTABLE**, initially **AWAITING_REFUND**, with 300 locked and zero slashed/refunded. A was recorded but its input URL returned a deterministic commit-pinned 404. A's semantic field is NOT_EVALUATED, effective verdict UNCLEAR, basis UNAVAILABLE_LOG. B's clear semantic violation did not cross the earlier uncertainty barrier. The early `settle_deadline()` attempt rolled back with `[EXPECTED] adjudication deadline not reached` and unchanged state. At/after J, deadline settlement entered **SETTLED_UNATTRIBUTABLE**, refunded every bond, preserved the complete original assessment, and slashed zero.

These cases demonstrate the difference from role-assigned blame that can charge contributors: an ordered vector drives one liable bond, with an earlier-uncertainty barrier. A later proven violation is retained even when it receives a refund or earlier uncertainty blocks blame.

## Deadlines — Africa/Lagos

- incident-3: recording deadline 2026-10-20T07:56:29+01:00; adjudication deadline 2026-10-20T08:00:29+01:00.
- incident-4: recording deadline 2026-10-20T07:58:48+01:00; adjudication deadline 2026-10-20T08:02:48+01:00.

## Stored per-step assessment

| Incident | Step | Evidence status | Semantic verdict | Effective verdict | Basis |
|---|---|---|---|---|---|
| incident-3 | A | AVAILABLE | FAITHFUL | FAITHFUL | SEMANTIC |
| incident-3 | B | AVAILABLE | VIOLATION | VIOLATION | SEMANTIC |
| incident-3 | C | AVAILABLE | VIOLATION | VIOLATION | SEMANTIC |
| incident-4 | A | UNAVAILABLE | NOT_EVALUATED | UNCLEAR | UNAVAILABLE_LOG |
| incident-4 | B | AVAILABLE | VIOLATION | VIOLATION | SEMANTIC |
| incident-4 | C | AVAILABLE | FAITHFUL | FAITHFUL | SEMANTIC |

## Global accounting

| Incident/stage | Phase | Deposited | Available | Locked | Slashed | Refunded |
|---|---|---:|---:|---:|---:|---:|
| incident-3 final | SETTLED_FAULT | 300 | 0 | 0 | 100 | 200 |
| incident-4 after adjudication | AWAITING_REFUND | 300 | 0 | 300 | 0 | 0 |
| incident-4 final | SETTLED_UNATTRIBUTABLE | 300 | 0 | 0 | 0 | 300 |

| Incident/stage | Operator | Deposited | Available | Locked | Slashed | Refunded |
|---|---|---:|---:|---:|---:|---:|
| incident-3 final | A | 100 | 0 | 0 | 0 | 100 |
| incident-3 final | B | 100 | 0 | 0 | 100 | 0 |
| incident-3 final | C | 100 | 0 | 0 | 0 | 100 |
| incident-4 after adjudication | A | 100 | 0 | 100 | 0 | 0 |
| incident-4 after adjudication | B | 100 | 0 | 100 | 0 | 0 |
| incident-4 after adjudication | C | 100 | 0 | 100 | 0 | 0 |
| incident-4 final | A | 100 | 0 | 0 | 0 | 100 |
| incident-4 final | B | 100 | 0 | 0 | 0 | 100 |
| incident-4 final | C | 100 | 0 | 0 | 0 | 100 |

Incident 3 claimant credit is 100; incident 4 claimant credit is zero. Every successful/rejected write was followed by both `get_state()` and `get_accounting()`. All 22 new readbacks pass global/per-owner conservation, nonnegativity, recipient-credit and exactly-once checks. Both final reads use latest-final state.

## Key Explorer transactions

- incident-3:deploy: [0x655facd22fcb82257a684bb85a23267cdb880d5c9a9127a02e80b7f753d6e997](https://explorer-studio.genlayer.com/tx/0x655facd22fcb82257a684bb85a23267cdb880d5c9a9127a02e80b7f753d6e997)
- incident-3:adjudicate: [0x25bf331a0ca6ce0b20584e5b0bef1c141e27404b99c1f6e6f4f7b295e35e8340](https://explorer-studio.genlayer.com/tx/0x25bf331a0ca6ce0b20584e5b0bef1c141e27404b99c1f6e6f4f7b295e35e8340)
- incident-4:deploy: [0xb66e3246f36571f3cf8c4be8f6d196f0c9743cc0b8b919ba01d45bb4ce2c2f05](https://explorer-studio.genlayer.com/tx/0xb66e3246f36571f3cf8c4be8f6d196f0c9743cc0b8b919ba01d45bb4ce2c2f05)
- incident-4:adjudicate: [0x28c756306b2c2b174684907986de4f8de284f46ec24e2fc9b437c395f7122cee](https://explorer-studio.genlayer.com/tx/0x28c756306b2c2b174684907986de4f8de284f46ec24e2fc9b437c395f7122cee)
- incident-4:early-timeout-rejected: [0x53029132bb7f7307e3c8da4ae2bfa5cd971b7375403099345c5cd39dc6df33fd](https://explorer-studio.genlayer.com/tx/0x53029132bb7f7307e3c8da4ae2bfa5cd971b7375403099345c5cd39dc6df33fd)
- incident-4:deadline-refund: [0x41d3ac16398fa62ab5db9ca4054903a4aefc76467315dfcd0b2bc0e9f92f9351](https://explorer-studio.genlayer.com/tx/0x41d3ac16398fa62ab5db9ca4054903a4aefc76467315dfcd0b2bc0e9f92f9351)

## All new transactions

All 20 are FINALIZED, with 19 SUCCESS/return executions and one labeled expected ERROR/rollback. ACCEPTED was directly observed for 20 of 20. The full manifest preserves raw and decoded receipts, actual lifecycle observations, execution payloads and votes for each hash; idle participants are not counted as agreeing validators.

| Operation | Transaction | ACCEPTED observed | Lifecycle | Leader execution/result | Votes | Expected result |
|---|---|---|---|---|---|---|
| incident-3:deploy | [0x655facd22fcb82257a684bb85a23267cdb880d5c9a9127a02e80b7f753d6e997](https://explorer-studio.genlayer.com/tx/0x655facd22fcb82257a684bb85a23267cdb880d5c9a9127a02e80b7f753d6e997) | yes | FINALIZED | SUCCESS/return | 5 agree | success |
| incident-3:deposit-A | [0x4fd38cd0c997dfd2cd86c0cfc01cafea8ad76e1bc854e19241a63a0f100522d0](https://explorer-studio.genlayer.com/tx/0x4fd38cd0c997dfd2cd86c0cfc01cafea8ad76e1bc854e19241a63a0f100522d0) | yes | FINALIZED | SUCCESS/return | 5 agree | success |
| incident-3:deposit-B | [0x6b22acae507699ee7f64ccc57095311f2717e12fc4df2f55d8803ad542cf6e1b](https://explorer-studio.genlayer.com/tx/0x6b22acae507699ee7f64ccc57095311f2717e12fc4df2f55d8803ad542cf6e1b) | yes | FINALIZED | SUCCESS/return | 5 agree | success |
| incident-3:deposit-C | [0x60ff4cac8f3387077be53a63b4de4d4c19989fbc17def5dfdcb1dfa8beb52647](https://explorer-studio.genlayer.com/tx/0x60ff4cac8f3387077be53a63b4de4d4c19989fbc17def5dfdcb1dfa8beb52647) | yes | FINALIZED | SUCCESS/return | 4 agree, 1 idle | success |
| incident-3:record-A | [0x07e38c2315b8f4f8071d54c3ef7845cfa542e5deaf4cc04837124d42f856ac85](https://explorer-studio.genlayer.com/tx/0x07e38c2315b8f4f8071d54c3ef7845cfa542e5deaf4cc04837124d42f856ac85) | yes | FINALIZED | SUCCESS/return | 3 agree, 2 idle | success |
| incident-3:record-B | [0xbddf1eeae51757db234c97636ea8e728cc70c97baea9400e8037bfa4e58557c9](https://explorer-studio.genlayer.com/tx/0xbddf1eeae51757db234c97636ea8e728cc70c97baea9400e8037bfa4e58557c9) | yes | FINALIZED | SUCCESS/return | 3 agree, 2 idle | success |
| incident-3:record-C | [0x2b22a492468ec6dbf699e8aca2c2ef4923d71f1ee476001b448a9e99aa92d1c7](https://explorer-studio.genlayer.com/tx/0x2b22a492468ec6dbf699e8aca2c2ef4923d71f1ee476001b448a9e99aa92d1c7) | yes | FINALIZED | SUCCESS/return | 3 agree, 2 idle | success |
| incident-4:deploy | [0xb66e3246f36571f3cf8c4be8f6d196f0c9743cc0b8b919ba01d45bb4ce2c2f05](https://explorer-studio.genlayer.com/tx/0xb66e3246f36571f3cf8c4be8f6d196f0c9743cc0b8b919ba01d45bb4ce2c2f05) | yes | FINALIZED | SUCCESS/return | 4 agree, 1 idle | success |
| incident-4:deposit-A | [0xe8bcae95f7c49e8006386babea8c24e27a7943a4820eb3879153751723b0967c](https://explorer-studio.genlayer.com/tx/0xe8bcae95f7c49e8006386babea8c24e27a7943a4820eb3879153751723b0967c) | yes | FINALIZED | SUCCESS/return | 4 agree, 1 idle | success |
| incident-4:deposit-B | [0x3a7af47dee5092d61a6e677e1319f86867bfe37c308dd2d1cee64a2174e4b284](https://explorer-studio.genlayer.com/tx/0x3a7af47dee5092d61a6e677e1319f86867bfe37c308dd2d1cee64a2174e4b284) | yes | FINALIZED | SUCCESS/return | 3 agree, 2 idle | success |
| incident-4:deposit-C | [0xb51f8c1f2ccd3cd166b3ac97774f3369b30ba7a40179d1b1aa8f703157da2303](https://explorer-studio.genlayer.com/tx/0xb51f8c1f2ccd3cd166b3ac97774f3369b30ba7a40179d1b1aa8f703157da2303) | yes | FINALIZED | SUCCESS/return | 3 agree, 2 idle | success |
| incident-4:record-A | [0x82c1847e635890962bd1721c00413ff9184c54213e2ff4d43fcf2b71e03eb634](https://explorer-studio.genlayer.com/tx/0x82c1847e635890962bd1721c00413ff9184c54213e2ff4d43fcf2b71e03eb634) | yes | FINALIZED | SUCCESS/return | 5 agree | success |
| incident-4:record-B | [0x033413b13aa0af07987cc0747078c31e6952f3d778c52441362c87608325930d](https://explorer-studio.genlayer.com/tx/0x033413b13aa0af07987cc0747078c31e6952f3d778c52441362c87608325930d) | yes | FINALIZED | SUCCESS/return | 5 agree | success |
| incident-4:record-C | [0x013698c93cdeefc1e9eeb0ea0ccb47987487a77a88998610b48bcf99098428f1](https://explorer-studio.genlayer.com/tx/0x013698c93cdeefc1e9eeb0ea0ccb47987487a77a88998610b48bcf99098428f1) | yes | FINALIZED | SUCCESS/return | 5 agree | success |
| incident-3:report | [0xef928fa23146f8507dc35f1072c08458a3c2de14d7fcdf270e0bbd7f16661a4a](https://explorer-studio.genlayer.com/tx/0xef928fa23146f8507dc35f1072c08458a3c2de14d7fcdf270e0bbd7f16661a4a) | yes | FINALIZED | SUCCESS/return | 3 agree, 2 idle | success |
| incident-3:adjudicate | [0x25bf331a0ca6ce0b20584e5b0bef1c141e27404b99c1f6e6f4f7b295e35e8340](https://explorer-studio.genlayer.com/tx/0x25bf331a0ca6ce0b20584e5b0bef1c141e27404b99c1f6e6f4f7b295e35e8340) | yes | FINALIZED | SUCCESS/return | 3 agree, 2 idle | success |
| incident-4:report | [0x3001dba485726423bb82ce244f7b87b45f32fddd4d3d4339fe20175838f9a9c0](https://explorer-studio.genlayer.com/tx/0x3001dba485726423bb82ce244f7b87b45f32fddd4d3d4339fe20175838f9a9c0) | yes | FINALIZED | SUCCESS/return | 3 agree, 2 idle | success |
| incident-4:adjudicate | [0x28c756306b2c2b174684907986de4f8de284f46ec24e2fc9b437c395f7122cee](https://explorer-studio.genlayer.com/tx/0x28c756306b2c2b174684907986de4f8de284f46ec24e2fc9b437c395f7122cee) | yes | FINALIZED | SUCCESS/return | 3 agree, 2 idle | success |
| incident-4:early-timeout-rejected | [0x53029132bb7f7307e3c8da4ae2bfa5cd971b7375403099345c5cd39dc6df33fd](https://explorer-studio.genlayer.com/tx/0x53029132bb7f7307e3c8da4ae2bfa5cd971b7375403099345c5cd39dc6df33fd) | yes | FINALIZED | ERROR/rollback | 4 agree, 1 idle | adjudication deadline not reached |
| incident-4:deadline-refund | [0x41d3ac16398fa62ab5db9ca4054903a4aefc76467315dfcd0b2bc0e9f92f9351](https://explorer-studio.genlayer.com/tx/0x41d3ac16398fa62ab5db9ca4054903a4aefc76467315dfcd0b2bc0e9f92f9351) | yes | FINALIZED | SUCCESS/return | 3 agree, 2 idle | success |

## Public response-body evidence

New public fixture commit: `eb57d011fdea6cc3a8ddc2fa0abe798075e8d297`. Eleven added fixture files contain only LF UTF-8 text. Every committed digest was measured from complete curl response bytes with no normalization or followed redirects. The intentionally absent A input was sampled twice as HTTP 404; its server error body has no trailing LF and is explicitly not presented as an eligible LF step log. Its committed digest hashes those exact server bytes; HTTP eligibility rejects it before integrity or semantic judgment. The missing path was never added to the public tree.

| Raw reference | HTTP | Response bytes | SHA-256 / committed digest | Line endings |
|---|---:|---:|---|---|
| [incident-3/A-input.txt](https://raw.githubusercontent.com/JWattjr/genlayer-demo-evidence/eb57d011fdea6cc3a8ddc2fa0abe798075e8d297/liability-cascade/incident-3/A-input.txt) | 200 | 128 | `54d8f95d0c1acd455817a557ccc83d1617f5149d71f0a0480e89bd121c83b7be` | LF |
| [incident-3/A-output.txt](https://raw.githubusercontent.com/JWattjr/genlayer-demo-evidence/eb57d011fdea6cc3a8ddc2fa0abe798075e8d297/liability-cascade/incident-3/A-output.txt) | 200 | 106 | `bce245bd4a29ad71fbc212eaf8c27ec10cf6a03b59a16aee7a435c02515cdd40` | LF |
| [incident-3/B-input.txt](https://raw.githubusercontent.com/JWattjr/genlayer-demo-evidence/eb57d011fdea6cc3a8ddc2fa0abe798075e8d297/liability-cascade/incident-3/B-input.txt) | 200 | 106 | `bce245bd4a29ad71fbc212eaf8c27ec10cf6a03b59a16aee7a435c02515cdd40` | LF |
| [incident-3/B-output.txt](https://raw.githubusercontent.com/JWattjr/genlayer-demo-evidence/eb57d011fdea6cc3a8ddc2fa0abe798075e8d297/liability-cascade/incident-3/B-output.txt) | 200 | 117 | `305cf384392bba47b66e6e99968aaa939da866aef2bb4e202f0c35edb5d4a2a0` | LF |
| [incident-3/C-input.txt](https://raw.githubusercontent.com/JWattjr/genlayer-demo-evidence/eb57d011fdea6cc3a8ddc2fa0abe798075e8d297/liability-cascade/incident-3/C-input.txt) | 200 | 117 | `305cf384392bba47b66e6e99968aaa939da866aef2bb4e202f0c35edb5d4a2a0` | LF |
| [incident-3/C-output.txt](https://raw.githubusercontent.com/JWattjr/genlayer-demo-evidence/eb57d011fdea6cc3a8ddc2fa0abe798075e8d297/liability-cascade/incident-3/C-output.txt) | 200 | 128 | `5072a43183332fdfbc1bd1bb4ec200ef1c4fab80e4140fd9ebfc6c0da99d9165` | LF |
| [incident-4/A-input-missing.txt](https://raw.githubusercontent.com/JWattjr/genlayer-demo-evidence/eb57d011fdea6cc3a8ddc2fa0abe798075e8d297/liability-cascade/incident-4/A-input-missing.txt) | 404 | 14 | `d5558cd419c8d46bdc958064cb97f963d1ea793866414c025906ec15033512ed` | SERVER_404_BODY_WITHOUT_TRAILING_LF |
| [incident-4/A-output.txt](https://raw.githubusercontent.com/JWattjr/genlayer-demo-evidence/eb57d011fdea6cc3a8ddc2fa0abe798075e8d297/liability-cascade/incident-4/A-output.txt) | 200 | 106 | `bce245bd4a29ad71fbc212eaf8c27ec10cf6a03b59a16aee7a435c02515cdd40` | LF |
| [incident-4/B-input.txt](https://raw.githubusercontent.com/JWattjr/genlayer-demo-evidence/eb57d011fdea6cc3a8ddc2fa0abe798075e8d297/liability-cascade/incident-4/B-input.txt) | 200 | 106 | `bce245bd4a29ad71fbc212eaf8c27ec10cf6a03b59a16aee7a435c02515cdd40` | LF |
| [incident-4/B-output.txt](https://raw.githubusercontent.com/JWattjr/genlayer-demo-evidence/eb57d011fdea6cc3a8ddc2fa0abe798075e8d297/liability-cascade/incident-4/B-output.txt) | 200 | 117 | `305cf384392bba47b66e6e99968aaa939da866aef2bb4e202f0c35edb5d4a2a0` | LF |
| [incident-4/C-input.txt](https://raw.githubusercontent.com/JWattjr/genlayer-demo-evidence/eb57d011fdea6cc3a8ddc2fa0abe798075e8d297/liability-cascade/incident-4/C-input.txt) | 200 | 117 | `305cf384392bba47b66e6e99968aaa939da866aef2bb4e202f0c35edb5d4a2a0` | LF |
| [incident-4/C-output.txt](https://raw.githubusercontent.com/JWattjr/genlayer-demo-evidence/eb57d011fdea6cc3a8ddc2fa0abe798075e8d297/liability-cascade/incident-4/C-output.txt) | 200 | 117 | `305cf384392bba47b66e6e99968aaa939da866aef2bb4e202f0c35edb5d4a2a0` | LF |

## Append-only provenance and verification

The existing manifest's original two incident objects, 26 transaction objects, 28 readbacks, original fixture evidence and all original top-level fields match release commit `87ab2d1ecf04c586527d36e297ca3d4bd9ec0356` exactly. New incident/transaction/readback objects were appended to those arrays; new evidence and run metadata are under `extension_runs`. Earlier receipts were not polled or rewritten. Original audit/docs remain historical evidence; this extension adds a separate independent audit.

- [Combined manifest](../deployments/studionet-release-2026-10-20.json)
- [Extension audit](../deployments/extension-audit-2026-10-20.json)
- [New curl measurements](../fixtures/evidence-extension-2026-10-20.json)
- [Original release audit](../deployments/release-audit-2026-10-20.json)

The combined release has four deployments, 46 FINALIZED transactions and 50 state/accounting readbacks. The original 193-test/lint verification remains unchanged because contract source is unchanged. Run `tools/audit_release.py` for the preserved original release, `tools/audit_extension.py` for the new incidents/preservation proof, and `tools/verify_remote.py` after the private push for remote/source equality. The contract repository stays PRIVATE. No key was printed or committed, and no Portal submission was made.
