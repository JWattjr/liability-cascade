"""Render release documentation only from independently audited live evidence."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
manifest_path = 'deployments/studionet-release-2026-10-20.json'
data = json.loads((ROOT / manifest_path).read_text(encoding='utf-8'))
audit = json.loads((ROOT / 'deployments/release-audit-2026-10-20.json').read_text(encoding='utf-8'))
assert data['status'] == 'LIVE_PASS' and audit['status'] == 'PASS'
assert not data.get('extension_runs'), 'Original documentation is archived; use tools/write_extension_docs.py for appended incidents'
txs = {t['operation']: t for t in data['transactions']}


def write(path, text):
    (ROOT / path).write_text(text.rstrip() + '\n', encoding='utf-8', newline='\n')


def link(transaction):
    return '[' + transaction['hash'] + '](' + transaction['explorer'] + ')'


incidents = []
for incident in data['incidents']:
    payer = ('A', 'B', 'C')[incident['expected_liable_index']]
    incidents.append('| ' + incident['id'] + ' | `' + incident['address'] + '` | ' + ', '.join(incident['expected_verdicts']) + ' | ' + payer + ' only: 100 slashed; 200 refunded | ' + link(txs[incident['id'] + ':adjudicate']) + ' |')
incident_table = '\n'.join(incidents)
roles = '\n'.join('| ' + role + ' | `' + info['alias'] + '` | `' + info['address'] + '` |' for role, info in data['participants'].items())
readme = f'''# Liability Cascade

Validators judge each ordered pipeline step against its own received input and frozen duty. Deterministic code selects the earliest proven violation, slashes only that operator's full synthetic bond to the nonoperator claimant, and refunds every other operator. An earlier unclear or unavailable step blocks attribution and leads to deadline refunds. The complete ordered assessment, including every evidence observation and local verdict, is compared exactly.

## Verified release — 2026-10-20

| Gate | Result | Evidence |
|---|---|---|
| Design and scoped distinctiveness | PASS | [DESIGN](docs/DESIGN.md), section 11: source-backed comparison with Faultline, SlashCourt, Evidence Retraction Registry, and Delegated Task Handoff |
| Code review, adversarial tests and lint | PASS | [REVIEW](docs/REVIEW.md); 193 tests, 0 failures/errors/skips; 3 AST checks and SDK validation passed |
| StudioNet source, execution, consensus and accounting | PASS | [Full manifest]({manifest_path}) and [independent release audit](deployments/release-audit-2026-10-20.json): 26 FINALIZED transactions, 18 successful executions, 8 expected rollbacks; 28 accounting/state readbacks |

The contract repository is **PRIVATE**. No Portal submission was made. Public evidence is fixture text only in [genlayer-demo-evidence](https://github.com/JWattjr/genlayer-demo-evidence/tree/{data['evidence']['fixture_commit']}/liability-cascade).

| Incident | Contract address | Stored A/B/C verdicts | Deterministic allocation | Finalized adjudication |
|---|---|---|---|---|
{incident_table}

Every configured operator deposited 100 synthetic units from its own sender address. The final deposit activated all bonds atomically. Both incidents rejected a nonoperator recording, a replacement recording, a configured operator's report, and post-settlement adjudication replay. Each rejected call preserved stored state and accounting. Every transaction's actual observed ACCEPTED/FINALIZED history, execution payload and validator votes is retained separately; lifecycle success is not used as a substitute for contract execution success.

## Source and fixture provenance

- Reviewed commit: `{data['review_commit']}`. The review added 75 adversarial regression cases and found no production-code defect in the reviewed consensus and settlement paths.
- Final regression-test blob: `{data['final_regression_tests_git_blob']}`, including the accepted-original-snapshot positive control before each foreign replay rejection. The final verification remains 193 passing cases.
- Deployment-source commit: `{data['source_commit']}`; contract Git blob `{data['source_blob']}`; SHA-256 `{data['source_sha256']}`. Both deployed sources match this blob byte-for-byte, including the final LF.
- Runner: `{data['runner']}`. The newer-runner notice is informational; the approved pin was retained.
- Public fixture commit: `{data['evidence']['fixture_commit']}`. `curl` fetched all 12 exact commit-pinned raw URLs with HTTP 200 and no followed redirects. Total body size: 1,404 bytes. Digests are over the exact served LF UTF-8 bytes; [measurement manifest](fixtures/evidence-manifest.json).
- Final publication adds the final replay-test refinement, documentation and receipts after the deployment-source commit. The single private push must contain that ancestor and the identical contract blob. The pushed release HEAD is reported separately; it is not falsely embedded in a commit that would have to contain its own SHA. `tools/verify_remote.py` verifies the private remote HEAD, ancestry and exact source bytes and saves an ignored local proof in `artifacts/remote-publication-verification.json` after the push.

## Demonstration policy and actors

The charter explicitly assigns source-email redaction to A. B uppercases names/regions and preserves contact values exactly as received, never restoring a value absent from its input. C reproduces received CSV bytes and has no independent filtering duty. Thus B/C can faithfully propagate inherited bad data in the A-fault incident. In the B-fault incident A redacts correctly, B restores an email, and C faithfully copies B's output. These are fictional example.org contacts, not real personal data.

| Role | Existing test-account alias | Public address |
|---|---|---|
{roles}

No keys or credentials are included. StudioNet is gasless; synthetic `deposit(100)` is a required contract participation action, not GEN funding.

## Local verification and interface

Use the existing pinned environment, without upgrades:

```powershell
& 'C:\\Users\\User\\Desktop\\Genlayer apps\\intelligent-contracts-v2\\.venv\\Scripts\\python.exe' tools/verify_local.py
& 'C:\\Users\\User\\Desktop\\Genlayer apps\\intelligent-contracts-v2\\.venv\\Scripts\\python.exe' tools/audit_release.py
```

Public writes: `deposit(amount_units)`, `record_step(step_id,input_url,output_url,input_digest,output_digest)`, `report_failure(final_output_url,description)`, `adjudicate()`, `settle_deadline()`. Views: `get_state()` and `get_accounting()`. All writes are nonpayable and reject terminal state. Exact typed signatures and the historical Phase 2 coverage map are in [PHASE2_HANDOFF](docs/PHASE2_HANDOFF.md). [TEST_MATRIX](docs/TEST_MATRIX.md) maps this release's local and live evidence.

The direct-mode Windows compatibility shim uses SDK v0.6.0-rc5 and explicit captured validator callbacks. Live execution uses genlayer-py 0.19.0rc2 with the scoped, copied license-bundle-clearinghouse calldata adapter for this exact StudioNet runner. It does not use the incompatible unadapted encoding path. The live runner saves each returned hash before polling and refuses an uncertain submission or a recorded unexpected judgment; never delete the manifest to retry a judgment.

## Limits

Bonds and payouts are synthetic units with no token custody. Fixture logs demonstrate classification; hashes prove byte consistency, not authentic execution or adjacent handoff continuity. Unavailable evidence before the first proven violation can block attribution; a permissionless transaction at/after the adjudication deadline refunds instead of proving innocence. Operator-address exclusion does not prevent an affiliated unconfigured claimant. URL syntax admission does not prove DNS/redirect publicness; this release uses only the measured commit-pinned raw GitHub URLs and claims no general network sandbox guarantee. Exact comparison can fail consensus when availability or semantic labels differ. The distinction from existing projects is scoped to the inspected local source snapshots, not global novelty.

See [evidence inventory](docs/EVIDENCE.md) and [owner-only submission draft](SUBMISSION_DRAFT.md). Keep this repository private; no visibility conversion or Portal action is part of this release.
'''
write('README.md', readme)

matrix = '''# Test matrix — reviewed StudioNet release

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
'''
write('docs/TEST_MATRIX.md', matrix)

fixture_rows = '\n'.join('| [' + f['path'] + '](' + f['raw_url'] + ') | ' + str(f['byte_length']) + ' | `' + f['sha256'] + '` |' for f in data['evidence']['fixtures'])
transaction_rows = '\n'.join('| ' + t['operation'] + ' | ' + link(t) + ' | ' + t['latest_status'] + ' | ' + t['leader_execution'] + '/' + t['leader_result_status'] + ' | ' + (t['expected_error'] or 'success') + ' |' for t in data['transactions'])
write('docs/EVIDENCE.md', f'''# Evidence inventory

- Full release manifest: [`{manifest_path}`](../{manifest_path}); independent audit: [release-audit](../deployments/release-audit-2026-10-20.json).
- Reviewed source commit `{data['review_commit']}`; deployment-source commit `{data['source_commit']}`; contract blob `{data['source_blob']}`; SHA-256 `{data['source_sha256']}`.
- Local verification outputs: [results](../verification/phase2-results.json), [pytest XML](../verification/pytest.xml), [lint](../verification/lint.stdout.txt), [schema](../verification/schema.json), [review](REVIEW.md).
- Public fixture repository commit `{data['evidence']['fixture_commit']}`, folder `liability-cascade/`; [curl measurement manifest](../fixtures/evidence-manifest.json). Other releases' text folders were preserved. This release added only twelve text artifacts.
- All 26 unique hashes are FINALIZED. ACCEPTED was directly observed for {audit['accepted_observed']} transactions; the manifest distinguishes actual observations from inference. Votes are counted per operation in the audit; idle/nonparticipating validators are not described as having agreed.
- All 28 state/accounting readbacks pass independent conservation/nonnegative/once-only checks. All eight expected failures preserve stored state. No Portal submission or repository visibility change was performed.
- One final read hit a transient HTTP 502. Only the missing latest-final readback was retried; no transaction or judgment was resubmitted. The recovered diagnostic remains in the manifest.

## Complete response-body measurements

HTTP 200 for every file, UTF-8 strict, LF only, no redirects followed; 1,404 exact bytes total.

| Raw fixture | Bytes | SHA-256 of served bytes |
|---|---:|---|
{fixture_rows}

## Transaction evidence

| Operation | Transaction | Lifecycle | Leader execution/result | Expected result |
|---|---|---|---|---|
{transaction_rows}

The manifest retains constructor arguments, all submitted arguments and actor aliases, full raw/decoded receipts, validator votes/receipts, source-byte checks, complete readbacks and every stored assessment. No lifecycle status is substituted for execution success. The local private release history contains the original deployment-source commit and the identical contract blob; final remote HEAD/source verification is performed after the single end-of-run push and reported to the owner.
''')

note = ('LIABILITY CASCADE: validators judge each ordered step against its received input and frozen duty. '
        'Deterministic code slashes only the earliest proven violator\'s full bond and refunds the others; earlier unclear or unavailable evidence blocks attribution. '
        'The whole assessment is compared exactly, with immutable input/output byte commitments. '
        'Two finalized StudioNet demos show B introducing an email while C faithfully propagates it, then A introducing one; only B and only A pay respectively. '
        'Limits: synthetic bonds and fictional fixture logs; hashes do not authenticate execution, unavailable logs can block blame, and address exclusion does not prove claimant independence.')
assert len(note) < 1000
write('SUBMISSION_DRAFT.md', '# Owner-only Portal draft\n\nNo submission has been made. The contract repository remains private.\n\n' + note + '\n\nCharacter count: ' + str(len(note)) + '.\n\nEvidence: [release manifest](' + manifest_path + '), [test matrix](docs/TEST_MATRIX.md), [review](docs/REVIEW.md), [evidence inventory](docs/EVIDENCE.md).')

design = (ROOT / 'docs/DESIGN.md').read_text(encoding='utf-8')
design = design.replace('live verification has not started.', 'the reviewed live release is documented in deployments/studionet-release-2026-10-20.json.')
lines = design.splitlines()
for index, line in enumerate(lines):
    if line.startswith('Pre-live gates:'):
        lines[index] = 'Final release gates: design/differentiation PASS, local review/tests/lint PASS (193 tests), live/source/finality PASS. The full release manifest records two byte-matched deployments, 26 FINALIZED transactions, eight expected rollbacks, stored judgments and 28 passing accounting readbacks. See REVIEW.md, TEST_MATRIX.md and EVIDENCE.md. The contract repository remains private; no Portal submission was made.'
write('docs/DESIGN.md', '\n'.join(lines))
print(json.dumps({'documentation': ['README.md', 'docs/TEST_MATRIX.md', 'docs/EVIDENCE.md', 'SUBMISSION_DRAFT.md', 'docs/DESIGN.md'], 'portal_note_characters': len(note), 'portal_submitted': False}))
