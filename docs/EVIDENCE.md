# Evidence inventory

- Full release manifest: [`deployments/studionet-release-2026-10-20.json`](../deployments/studionet-release-2026-10-20.json); independent audit: [release-audit](../deployments/release-audit-2026-10-20.json).
- Reviewed source commit `2619c4e7b2963117571f383ee8ef1dff9b2d7c07`; deployment-source commit `da39762abefd3027ab72d47821c06313db1e1993`; contract blob `53ff0f7eb7b7be57115886476c55e282b8ab3492`; SHA-256 `b5118d6cd32ef3a642795b4e046fa0bdc13b9f60960fd900833d7e80962dff40`.
- Local verification outputs: [results](../verification/phase2-results.json), [pytest XML](../verification/pytest.xml), [lint](../verification/lint.stdout.txt), [schema](../verification/schema.json), [review](REVIEW.md).
- Public fixture repository commit `61b7d56d8147e0f97d89b4e8f4b424141ebaff3c`, folder `liability-cascade/`; [curl measurement manifest](../fixtures/evidence-manifest.json). Other releases' text folders were preserved. This release added only twelve text artifacts.
- All 26 unique hashes are FINALIZED. ACCEPTED was directly observed for 26 transactions; the manifest distinguishes actual observations from inference. Votes are counted per operation in the audit; idle/nonparticipating validators are not described as having agreed.
- All 28 state/accounting readbacks pass independent conservation/nonnegative/once-only checks. All eight expected failures preserve stored state. No Portal submission or repository visibility change was performed.
- One final read hit a transient HTTP 502. Only the missing latest-final readback was retried; no transaction or judgment was resubmitted. The recovered diagnostic remains in the manifest.

## Complete response-body measurements

HTTP 200 for every file, UTF-8 strict, LF only, no redirects followed; 1,404 exact bytes total.

| Raw fixture | Bytes | SHA-256 of served bytes |
|---|---:|---|
| [incident-a/A-input.txt](https://raw.githubusercontent.com/JWattjr/genlayer-demo-evidence/61b7d56d8147e0f97d89b4e8f4b424141ebaff3c/liability-cascade/incident-a/A-input.txt) | 128 | `54d8f95d0c1acd455817a557ccc83d1617f5149d71f0a0480e89bd121c83b7be` |
| [incident-a/A-output.txt](https://raw.githubusercontent.com/JWattjr/genlayer-demo-evidence/61b7d56d8147e0f97d89b4e8f4b424141ebaff3c/liability-cascade/incident-a/A-output.txt) | 117 | `697c66d7f098b2cfa4a9213c8322532e774acc2eceffb33c51a254de2af81c5d` |
| [incident-a/B-input.txt](https://raw.githubusercontent.com/JWattjr/genlayer-demo-evidence/61b7d56d8147e0f97d89b4e8f4b424141ebaff3c/liability-cascade/incident-a/B-input.txt) | 117 | `697c66d7f098b2cfa4a9213c8322532e774acc2eceffb33c51a254de2af81c5d` |
| [incident-a/B-output.txt](https://raw.githubusercontent.com/JWattjr/genlayer-demo-evidence/61b7d56d8147e0f97d89b4e8f4b424141ebaff3c/liability-cascade/incident-a/B-output.txt) | 117 | `305cf384392bba47b66e6e99968aaa939da866aef2bb4e202f0c35edb5d4a2a0` |
| [incident-a/C-input.txt](https://raw.githubusercontent.com/JWattjr/genlayer-demo-evidence/61b7d56d8147e0f97d89b4e8f4b424141ebaff3c/liability-cascade/incident-a/C-input.txt) | 117 | `305cf384392bba47b66e6e99968aaa939da866aef2bb4e202f0c35edb5d4a2a0` |
| [incident-a/C-output.txt](https://raw.githubusercontent.com/JWattjr/genlayer-demo-evidence/61b7d56d8147e0f97d89b4e8f4b424141ebaff3c/liability-cascade/incident-a/C-output.txt) | 117 | `305cf384392bba47b66e6e99968aaa939da866aef2bb4e202f0c35edb5d4a2a0` |
| [incident-b/A-input.txt](https://raw.githubusercontent.com/JWattjr/genlayer-demo-evidence/61b7d56d8147e0f97d89b4e8f4b424141ebaff3c/liability-cascade/incident-b/A-input.txt) | 128 | `54d8f95d0c1acd455817a557ccc83d1617f5149d71f0a0480e89bd121c83b7be` |
| [incident-b/A-output.txt](https://raw.githubusercontent.com/JWattjr/genlayer-demo-evidence/61b7d56d8147e0f97d89b4e8f4b424141ebaff3c/liability-cascade/incident-b/A-output.txt) | 106 | `bce245bd4a29ad71fbc212eaf8c27ec10cf6a03b59a16aee7a435c02515cdd40` |
| [incident-b/B-input.txt](https://raw.githubusercontent.com/JWattjr/genlayer-demo-evidence/61b7d56d8147e0f97d89b4e8f4b424141ebaff3c/liability-cascade/incident-b/B-input.txt) | 106 | `bce245bd4a29ad71fbc212eaf8c27ec10cf6a03b59a16aee7a435c02515cdd40` |
| [incident-b/B-output.txt](https://raw.githubusercontent.com/JWattjr/genlayer-demo-evidence/61b7d56d8147e0f97d89b4e8f4b424141ebaff3c/liability-cascade/incident-b/B-output.txt) | 117 | `305cf384392bba47b66e6e99968aaa939da866aef2bb4e202f0c35edb5d4a2a0` |
| [incident-b/C-input.txt](https://raw.githubusercontent.com/JWattjr/genlayer-demo-evidence/61b7d56d8147e0f97d89b4e8f4b424141ebaff3c/liability-cascade/incident-b/C-input.txt) | 117 | `305cf384392bba47b66e6e99968aaa939da866aef2bb4e202f0c35edb5d4a2a0` |
| [incident-b/C-output.txt](https://raw.githubusercontent.com/JWattjr/genlayer-demo-evidence/61b7d56d8147e0f97d89b4e8f4b424141ebaff3c/liability-cascade/incident-b/C-output.txt) | 117 | `305cf384392bba47b66e6e99968aaa939da866aef2bb4e202f0c35edb5d4a2a0` |

## Transaction evidence

| Operation | Transaction | Lifecycle | Leader execution/result | Expected result |
|---|---|---|---|---|
| incident-b:deploy | [0x84cc5e4821a48b735b73a42e3234911479ef0cf3f84e112eb9fc226634ce2b29](https://explorer-studio.genlayer.com/tx/0x84cc5e4821a48b735b73a42e3234911479ef0cf3f84e112eb9fc226634ce2b29) | FINALIZED | SUCCESS/return | success |
| incident-b:deposit-A | [0xb698547e9844258774c63dbc2bf4f6aefe1b672d9cc234368137e3146f92a391](https://explorer-studio.genlayer.com/tx/0xb698547e9844258774c63dbc2bf4f6aefe1b672d9cc234368137e3146f92a391) | FINALIZED | SUCCESS/return | success |
| incident-b:deposit-B | [0x69bc8b56c8dd7bfcfc22697a7c7e744ce0370214cbd8d4018e298d8d687ee97c](https://explorer-studio.genlayer.com/tx/0x69bc8b56c8dd7bfcfc22697a7c7e744ce0370214cbd8d4018e298d8d687ee97c) | FINALIZED | SUCCESS/return | success |
| incident-b:deposit-C | [0x7c9f01b11bdadb20572899f467d109629129317ca6ac2665cb54ce6de81987db](https://explorer-studio.genlayer.com/tx/0x7c9f01b11bdadb20572899f467d109629129317ca6ac2665cb54ce6de81987db) | FINALIZED | SUCCESS/return | success |
| incident-b:wrong-caller-record | [0x90b1063a0a539c373f301a75d7d39cfdc73ef4256761340a25f67915b4f8cb09](https://explorer-studio.genlayer.com/tx/0x90b1063a0a539c373f301a75d7d39cfdc73ef4256761340a25f67915b4f8cb09) | FINALIZED | ERROR/rollback | only assigned operator may record |
| incident-b:record-A | [0x2fe72639a37df64582fada5dd63a758554f992987b4ff66891571d4aa363d561](https://explorer-studio.genlayer.com/tx/0x2fe72639a37df64582fada5dd63a758554f992987b4ff66891571d4aa363d561) | FINALIZED | SUCCESS/return | success |
| incident-b:replacement-rejected | [0x7ed54f3daf0f9b7217ba55a1e77b4e4d2b865cd24ab03b780f1dd4e1d15f501d](https://explorer-studio.genlayer.com/tx/0x7ed54f3daf0f9b7217ba55a1e77b4e4d2b865cd24ab03b780f1dd4e1d15f501d) | FINALIZED | ERROR/rollback | step already recorded |
| incident-b:record-B | [0x2d982a2cf41c318d82bfedd4383437adde3a146aea2cacabe93febd774a9d1d6](https://explorer-studio.genlayer.com/tx/0x2d982a2cf41c318d82bfedd4383437adde3a146aea2cacabe93febd774a9d1d6) | FINALIZED | SUCCESS/return | success |
| incident-b:record-C | [0xaab16c1378529e967499460de8e3af6b32ce4a7c7a93f52467c2224c24bdd872](https://explorer-studio.genlayer.com/tx/0xaab16c1378529e967499460de8e3af6b32ce4a7c7a93f52467c2224c24bdd872) | FINALIZED | SUCCESS/return | success |
| incident-a:deploy | [0xfa78dce9ddf51b384b51d538e7385c77d4e0f7b71939daf4b6be1ac70b946317](https://explorer-studio.genlayer.com/tx/0xfa78dce9ddf51b384b51d538e7385c77d4e0f7b71939daf4b6be1ac70b946317) | FINALIZED | SUCCESS/return | success |
| incident-a:deposit-A | [0xb2ae9127c59c9ac70148a3c6b36b149062ac5ba77ee45e6285233efba4e3f7bd](https://explorer-studio.genlayer.com/tx/0xb2ae9127c59c9ac70148a3c6b36b149062ac5ba77ee45e6285233efba4e3f7bd) | FINALIZED | SUCCESS/return | success |
| incident-a:deposit-B | [0xc7428614e6b86929d9b59621842801ad6811de8f2481778335e6526c2f57c9e8](https://explorer-studio.genlayer.com/tx/0xc7428614e6b86929d9b59621842801ad6811de8f2481778335e6526c2f57c9e8) | FINALIZED | SUCCESS/return | success |
| incident-a:deposit-C | [0x164d6a266cc8227a481d30a5dff15eafee8c36c9806b420328ed346e8a314382](https://explorer-studio.genlayer.com/tx/0x164d6a266cc8227a481d30a5dff15eafee8c36c9806b420328ed346e8a314382) | FINALIZED | SUCCESS/return | success |
| incident-a:wrong-caller-record | [0x7c8fe253aeb15c6acdf84dd93426065fd960e2fece3c5690ef260f5fae28282f](https://explorer-studio.genlayer.com/tx/0x7c8fe253aeb15c6acdf84dd93426065fd960e2fece3c5690ef260f5fae28282f) | FINALIZED | ERROR/rollback | only assigned operator may record |
| incident-a:record-A | [0xb9b9de9ccdd36e1d00f28d482108bb9c43cb8c24b37e104a7b41e7ed18202c2d](https://explorer-studio.genlayer.com/tx/0xb9b9de9ccdd36e1d00f28d482108bb9c43cb8c24b37e104a7b41e7ed18202c2d) | FINALIZED | SUCCESS/return | success |
| incident-a:replacement-rejected | [0x5c54f4e03e74ff3e49c95c73bbaa37d90f343adde18a26de0f878585767de97c](https://explorer-studio.genlayer.com/tx/0x5c54f4e03e74ff3e49c95c73bbaa37d90f343adde18a26de0f878585767de97c) | FINALIZED | ERROR/rollback | step already recorded |
| incident-a:record-B | [0xd5d251f068c83cfb778c0150a1f7f07c0cab0578b67512db1c7b75355dd9b528](https://explorer-studio.genlayer.com/tx/0xd5d251f068c83cfb778c0150a1f7f07c0cab0578b67512db1c7b75355dd9b528) | FINALIZED | SUCCESS/return | success |
| incident-a:record-C | [0xa16836c6ed2448326b3f2be1e31be4b74ec65cc01a6c5797273b0636c61f390f](https://explorer-studio.genlayer.com/tx/0xa16836c6ed2448326b3f2be1e31be4b74ec65cc01a6c5797273b0636c61f390f) | FINALIZED | SUCCESS/return | success |
| incident-b:operator-claim-rejected | [0x49eec40a027182bab92e4d7685715904b55e5bf1a3a4406589658cd4d2d27f14](https://explorer-studio.genlayer.com/tx/0x49eec40a027182bab92e4d7685715904b55e5bf1a3a4406589658cd4d2d27f14) | FINALIZED | ERROR/rollback | configured operator cannot be claimant |
| incident-b:report | [0xbce1a07aff34675b798c7c079c483900c4239205e03371393738b127abcd1c3e](https://explorer-studio.genlayer.com/tx/0xbce1a07aff34675b798c7c079c483900c4239205e03371393738b127abcd1c3e) | FINALIZED | SUCCESS/return | success |
| incident-b:adjudicate | [0x5cfa5a00f6e7718749763ad326e314a79df5175fbb8304efa59550d69c53610c](https://explorer-studio.genlayer.com/tx/0x5cfa5a00f6e7718749763ad326e314a79df5175fbb8304efa59550d69c53610c) | FINALIZED | SUCCESS/return | success |
| incident-b:replay-rejected | [0x16a7e8e2b84a1737e53d86a013449edc31b072b91cb83b4f36703411f5a31eb3](https://explorer-studio.genlayer.com/tx/0x16a7e8e2b84a1737e53d86a013449edc31b072b91cb83b4f36703411f5a31eb3) | FINALIZED | ERROR/rollback | terminal state |
| incident-a:operator-claim-rejected | [0x99d0310f7785c76dbd8f5d3f76079777a72cca7de8ce4610dc59a5e3ee070453](https://explorer-studio.genlayer.com/tx/0x99d0310f7785c76dbd8f5d3f76079777a72cca7de8ce4610dc59a5e3ee070453) | FINALIZED | ERROR/rollback | configured operator cannot be claimant |
| incident-a:report | [0x4c83088020f6da66eb5b5dd28d986044135fe91435f0ed835cec50a7c9685ab7](https://explorer-studio.genlayer.com/tx/0x4c83088020f6da66eb5b5dd28d986044135fe91435f0ed835cec50a7c9685ab7) | FINALIZED | SUCCESS/return | success |
| incident-a:adjudicate | [0x4991aa213147a803c956e1e2315c2857fa6fd4d6d5368d6527b39b17df8bc2fa](https://explorer-studio.genlayer.com/tx/0x4991aa213147a803c956e1e2315c2857fa6fd4d6d5368d6527b39b17df8bc2fa) | FINALIZED | SUCCESS/return | success |
| incident-a:replay-rejected | [0xa23a0ac19b28871d34537c41c29512b105d319acaca4b47ee2e83ffe47ae0c44](https://explorer-studio.genlayer.com/tx/0xa23a0ac19b28871d34537c41c29512b105d319acaca4b47ee2e83ffe47ae0c44) | FINALIZED | ERROR/rollback | terminal state |

The manifest retains constructor arguments, all submitted arguments and actor aliases, full raw/decoded receipts, validator votes/receipts, source-byte checks, complete readbacks and every stored assessment. No lifecycle status is substituted for execution success. The local private release history contains the original deployment-source commit and the identical contract blob; final remote HEAD/source verification is performed after the single end-of-run push and reported to the owner.
