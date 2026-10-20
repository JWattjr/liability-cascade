# Test matrix — reviewed StudioNet release

Pinned environment and exact results: **193 passed, 0 failed, 0 errors, 0 skipped; 3 AST lint checks and SDK semantic validation passed**. See `verification/` and `docs/REVIEW.md`. The original handoff's 118 cases remain historical; the review adds 75.

| Requirement | Direct-mode evidence | Live evidence |
|---|---|---|
| B fault, faithful C; only B slashed | `test_settlement_allocates_only_earliest_bond[B-fault-C-faithful]` | incident-b finalized vector FAITHFUL/VIOLATION/FAITHFUL; B slash 100, A/C refunds 100 each |
| A fault; only A slashed | `test_settlement_allocates_only_earliest_bond[A-fault]` | incident-a finalized vector VIOLATION/FAITHFUL/FAITHFUL; A slash 100, B/C refunds 100 each |
| All faithful, one slash maximum, uncertainty before/after fault | Settlement and earlier-uncertainty parametrizations | The two required incident allocations; other semantic scenarios local only |
| Every stored consensus field bound | 68 leaf mutations and existing envelope/observation schema forgeries invoke actual callback | Stored whole vectors, complete observations, receipt digests, and recorded votes from the hosted runner |
| Valid foreign result cannot replay | 5 foreign-snapshot candidates, same payer, rejected by actual callback | Distinct deployment-bound snapshot digests in the two incidents |
| Independent validator work | Spy confirms `_assess` invocation for a schema-valid same-payer forgery; changed-fetch tests | Validator votes/receipts and nondeterministic outputs in the full manifest |
| Model cannot choose payout/status | Extra-key/model-error tests; exact schema and code-derived allocation review | Stored labels mapped by deterministic code to the expected exact allocation |
| Own deposits; all operators must fund | Partial/excess/zero/bool deposit, funding cancellation and activation tests | Three own-sender deposits per incident, activation on the third |
| Exact integer conservation and nonnegativity | Every successful/rejected helper; unequal/max bonds (1,10**18,7) | 28 independent state/accounting audits; terminal 300=100 slashed+200 refunded per incident |
| Wrong caller, immutable recording | Wrong-caller and duplicate-record tests | Wrong caller and changed-digest replacement both roll back in each incident; state unchanged |
| Configured operators cannot claim | All three configured operator addresses revert; independent report succeeds | A's report rolls back in each incident; fourth-account claimant succeeds |
| One incident, one assessment, one settlement; terminal replay | Every terminal write across all four terminal states; second report/adjudication tests | Post-settlement adjudication replays roll back in both incidents; counters remain one |
| Deadline edges and timeout liveness | At R/J boundaries, no-report/no-assessment refund, AWAITING_REFUND rules | Reporting waited for frozen R; exact boundary and timeout branches covered locally, not claimed live |
| Evidence failures/misconduct | Non-200, empty, whitespace, 15001 bytes, invalid UTF-8, transport, missing and tampered logs; 15000 accepted | All twelve live artifacts HTTP 200, digest-matched and available; outage branches local only |
| Immutable source and complete fixture bytes | Pinned header/schema/LF verification | Two on-chain sources match source-commit blob; curl byte counts and hashes match all committed LF fixture files |
| Actual lifecycle vs execution | Local mocks do not establish live finality | All 26 transactions FINALIZED: 18 SUCCESS/return and 8 ERROR/rollback; observed acceptance retained separately |

All exact local test names and the full design requirement mapping remain in `docs/PHASE2_HANDOFF.md` and `docs/REVIEW.md`. Live hashes, actor addresses, constructor deadlines, every vote and every readback are in `deployments/studionet-release-2026-10-20.json`; `deployments/release-audit-2026-10-20.json` rechecks counts and unchanged rejected-call state without submitting transactions.

## Additional live incidents 3 and 4

- [0x56e7E3b200bD95ef44cea1a71cc3a626026E103f](https://explorer-studio.genlayer.com/address/0x56e7E3b200bD95ef44cea1a71cc3a626026E103f) — incident-3
- [0x580326cD677EE0a613Aa4efAeb648A3cfa8Ed2A4](https://explorer-studio.genlayer.com/address/0x580326cD677EE0a613Aa4efAeb648A3cfa8Ed2A4) — incident-4

Incident 3: **FAITHFUL / VIOLATION / VIOLATION → PIPELINE_FAULT**; only B slashed 100, A/C refunded 100 each, with C's VIOLATION retained. Incident 4: **UNCLEAR (UNAVAILABLE 404) / VIOLATION / FAITHFUL → UNATTRIBUTABLE**, AWAITING_REFUND with nobody slashed; early timeout reverted; deadline settlement refunded all 300 with zero slash and preserved the assessment.

Both deploy the exact unchanged `da39762` source blob. New evidence commit `eb57d011fdea6cc3a8ddc2fa0abe798075e8d297` contains eleven LF text logs; the twelfth input reference deliberately returns 404. Twenty new transactions are FINALIZED (19 successful executions, one expected rollback), with 22 passing new readbacks. **Combined coverage: four deployments, 46 FINALIZED transactions, 50 passing readbacks.**

The original sections above are preserved. See [complete extension evidence](LIVE_EXTENSIONS.md), [extension audit](../deployments/extension-audit-2026-10-20.json), and [combined manifest](../deployments/studionet-release-2026-10-20.json). The private repository/source equality is checked after publication; no Portal submission is made.
