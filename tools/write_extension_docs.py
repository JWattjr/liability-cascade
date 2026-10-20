"""Append audited live evidence without replacing the original release sections."""
import json
import subprocess
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = '87ab2d1ecf04c586527d36e297ca3d4bd9ec0356'
MANIFEST = 'deployments/studionet-release-2026-10-20.json'


def write(path, text):
    (ROOT / path).write_text(text.rstrip() + '\n', encoding='utf-8', newline='\n')


def main():
    data = json.loads((ROOT / MANIFEST).read_text(encoding='utf-8'))
    audit = json.loads((ROOT / 'deployments/extension-audit-2026-10-20.json').read_text(encoding='utf-8'))
    assert audit['status'] == 'PASS'
    run = next(row for row in data['extension_runs'] if row['id'] == 'incidents-3-and-4')
    assert run['status'] == 'LIVE_PASS'
    incidents = data['incidents'][2:]
    transactions = data['transactions'][26:]
    readings = data['readbacks'][28:]
    by_name = {row['operation']: row for row in transactions}

    def tx(row):
        return '[' + row['hash'] + '](' + row['explorer'] + ')'

    def address(incident):
        return '[' + incident['address'] + '](https://explorer-studio.genlayer.com/address/' + incident['address'] + ')'

    def clock(value):
        return datetime.fromtimestamp(value, timezone(timedelta(hours=1))).isoformat()

    addresses = '\n'.join('- ' + address(incident) + ' — ' + incident['id'] for incident in incidents)
    verdict_rows = []
    accounting_rows = []
    global_rows = []
    for incident in incidents:
        final = next(row for row in readings if row['after'] == incident['id'] + ':finalized-audit')
        for step in final['state']['assessment']['steps']:
            verdict_rows.append('| ' + incident['id'] + ' | ' + step['step_id'] + ' | ' + step['evidence_status'] + ' | ' + step['semantic_verdict'] + ' | ' + step['effective_verdict'] + ' | ' + step['basis'] + ' |')
        stages = [('final', final)]
        if incident['id'] == 'incident-4':
            stages.insert(0, ('after adjudication', next(row for row in readings if row['after'] == 'incident-4:adjudicate')))
        for stage, reading in stages:
            totals = reading['accounting']['totals']
            global_rows.append('| ' + incident['id'] + ' ' + stage + ' | ' + reading['state']['phase'] + ' | ' + ' | '.join(str(totals[key]) for key in ('deposited', 'available', 'locked', 'slashed', 'refunded')) + ' |')
            for step in reading['state']['config']['steps']:
                row = reading['state']['ledger'][step['operator']]
                accounting_rows.append('| ' + incident['id'] + ' ' + stage + ' | ' + step['step_id'] + ' | ' + ' | '.join(str(row[key]) for key in ('deposited', 'available', 'locked', 'slashed', 'refunded')) + ' |')
    transaction_rows = []
    for row in transactions:
        votes = ', '.join(str(count) + ' ' + vote for vote, count in sorted(Counter(row['validator_votes'].values()).items()))
        transaction_rows.append('| ' + row['operation'] + ' | ' + tx(row) + ' | ' + ('yes' if row['accepted_observed'] else 'not observed') + ' | ' + row['latest_status'] + ' | ' + row['leader_execution'] + '/' + row['leader_result_status'] + ' | ' + votes + ' | ' + (row['expected_error'] or 'success') + ' |')
    fixture_rows = '\n'.join('| [' + row['path'] + '](' + row['raw_url'] + ') | ' + str(row['http_status']) + ' | ' + str(row['byte_length']) + ' | `' + row['sha256'] + '` | ' + row['line_endings'] + ' |' for row in run['evidence']['fixtures'])
    deadlines = '\n'.join('- ' + row['id'] + ': recording deadline ' + clock(row['recording_deadline']) + '; adjudication deadline ' + clock(row['adjudication_deadline']) + '.' for row in incidents)
    keys = '\n'.join('- ' + name + ': ' + tx(by_name[name]) for name in ('incident-3:deploy', 'incident-3:adjudicate', 'incident-4:deploy', 'incident-4:adjudicate', 'incident-4:early-timeout-rejected', 'incident-4:deadline-refund'))
    body = f'''# Additional live incidents 3 and 4

{addresses}

Both deployed from the exact source at `da39762abefd3027ab72d47821c06313db1e1993`, contract blob `{data['source_blob']}`, SHA-256 `{data['source_sha256']}`. Both on-chain bodies match that blob byte-for-byte. No contract source was changed. The same three operator accounts and distinct fourth-account claimant were used.

## Results and the allocation distinction

Incident 3 stored **A FAITHFUL, B VIOLATION, C VIOLATION**, outcome **PIPELINE_FAULT**, phase **SETTLED_FAULT**. Only B lost its 100-unit bond. A and C each received a 100-unit refund. C's stored semantic/effective VIOLATION remains visible: its refund follows the single-earliest-payer allocation rule and is not a finding that C was faithful. B restored Leah's email; C independently restored Theo's email absent from C's input.

Incident 4 stored **A UNCLEAR/UNAVAILABLE, B VIOLATION, C FAITHFUL**, outcome **UNATTRIBUTABLE**, initially **AWAITING_REFUND**, with 300 locked and zero slashed/refunded. A was recorded but its input URL returned a deterministic commit-pinned 404. A's semantic field is NOT_EVALUATED, effective verdict UNCLEAR, basis UNAVAILABLE_LOG. B's clear semantic violation did not cross the earlier uncertainty barrier. The early `settle_deadline()` attempt rolled back with `[EXPECTED] adjudication deadline not reached` and unchanged state. At/after J, deadline settlement entered **SETTLED_UNATTRIBUTABLE**, refunded every bond, preserved the complete original assessment, and slashed zero.

These cases demonstrate the difference from role-assigned blame that can charge contributors: an ordered vector drives one liable bond, with an earlier-uncertainty barrier. A later proven violation is retained even when it receives a refund or earlier uncertainty blocks blame.

## Deadlines — Africa/Lagos

{deadlines}

## Stored per-step assessment

| Incident | Step | Evidence status | Semantic verdict | Effective verdict | Basis |
|---|---|---|---|---|---|
{chr(10).join(verdict_rows)}

## Global accounting

| Incident/stage | Phase | Deposited | Available | Locked | Slashed | Refunded |
|---|---|---:|---:|---:|---:|---:|
{chr(10).join(global_rows)}

| Incident/stage | Operator | Deposited | Available | Locked | Slashed | Refunded |
|---|---|---:|---:|---:|---:|---:|
{chr(10).join(accounting_rows)}

Incident 3 claimant credit is 100; incident 4 claimant credit is zero. Every successful/rejected write was followed by both `get_state()` and `get_accounting()`. All 22 new readbacks pass global/per-owner conservation, nonnegativity, recipient-credit and exactly-once checks. Both final reads use latest-final state.

## Key Explorer transactions

{keys}

## All new transactions

All 20 are FINALIZED, with 19 SUCCESS/return executions and one labeled expected ERROR/rollback. ACCEPTED was directly observed for {audit['new_accepted_observed']} of 20. The full manifest preserves raw and decoded receipts, actual lifecycle observations, execution payloads and votes for each hash; idle participants are not counted as agreeing validators.

| Operation | Transaction | ACCEPTED observed | Lifecycle | Leader execution/result | Votes | Expected result |
|---|---|---|---|---|---|---|
{chr(10).join(transaction_rows)}

## Public response-body evidence

New public fixture commit: `{run['evidence']['fixture_commit']}`. Eleven added fixture files contain only LF UTF-8 text. Every committed digest was measured from complete curl response bytes with no normalization or followed redirects. The intentionally absent A input was sampled twice as HTTP 404; its server error body has no trailing LF and is explicitly not presented as an eligible LF step log. Its committed digest hashes those exact server bytes; HTTP eligibility rejects it before integrity or semantic judgment. The missing path was never added to the public tree.

| Raw reference | HTTP | Response bytes | SHA-256 / committed digest | Line endings |
|---|---:|---:|---|---|
{fixture_rows}

## Append-only provenance and verification

The existing manifest's original two incident objects, 26 transaction objects, 28 readbacks, original fixture evidence and all original top-level fields match release commit `{BASE}` exactly. New incident/transaction/readback objects were appended to those arrays; new evidence and run metadata are under `extension_runs`. Earlier receipts were not polled or rewritten. Original audit/docs remain historical evidence; this extension adds a separate independent audit.

- [Combined manifest](../{MANIFEST})
- [Extension audit](../deployments/extension-audit-2026-10-20.json)
- [New curl measurements](../fixtures/evidence-extension-2026-10-20.json)
- [Original release audit](../deployments/release-audit-2026-10-20.json)

The combined release has four deployments, 46 FINALIZED transactions and 50 state/accounting readbacks. The original 193-test/lint verification remains unchanged because contract source is unchanged. Run `tools/audit_release.py` for the preserved original release, `tools/audit_extension.py` for the new incidents/preservation proof, and `tools/verify_remote.py` after the private push for remote/source equality. The contract repository stays PRIVATE. No key was printed or committed, and no Portal submission was made.
'''
    write('docs/LIVE_EXTENSIONS.md', body)

    def append(path, extension):
        original = subprocess.run(['git', 'show', BASE + ':' + path], cwd=ROOT, capture_output=True, check=True).stdout.decode('utf-8')
        existing = (ROOT / path).read_text(encoding='utf-8')
        assert existing == original or existing.startswith(original + '\n## Additional live incidents 3 and 4')
        write(path, original + '\n' + extension)

    compact = f'''## Additional live incidents 3 and 4

{addresses}

Incident 3: **FAITHFUL / VIOLATION / VIOLATION → PIPELINE_FAULT**; only B slashed 100, A/C refunded 100 each, with C's VIOLATION retained. Incident 4: **UNCLEAR (UNAVAILABLE 404) / VIOLATION / FAITHFUL → UNATTRIBUTABLE**, AWAITING_REFUND with nobody slashed; early timeout reverted; deadline settlement refunded all 300 with zero slash and preserved the assessment.

Both deploy the exact unchanged `da39762` source blob. New evidence commit `{run['evidence']['fixture_commit']}` contains eleven LF text logs; the twelfth input reference deliberately returns 404. Twenty new transactions are FINALIZED (19 successful executions, one expected rollback), with 22 passing new readbacks. **Combined coverage: four deployments, 46 FINALIZED transactions, 50 passing readbacks.**

The original sections above are preserved. See [complete extension evidence](LIVE_EXTENSIONS.md), [extension audit](../deployments/extension-audit-2026-10-20.json), and [combined manifest](../{MANIFEST}). The private repository/source equality is checked after publication; no Portal submission is made.
'''
    for path in ('docs/EVIDENCE.md', 'docs/TEST_MATRIX.md'):
        append(path, compact)
    append('README.md', compact.replace('(LIVE_EXTENSIONS.md)', '(docs/LIVE_EXTENSIONS.md)').replace('(../deployments/', '(deployments/'))
    note = ("LIABILITY CASCADE: validators compare the whole vector of input-conditioned local verdicts; deterministic code selects the earliest proven violation, slashes one full bond, and refunds the others. "
        "Four finalized StudioNet incidents show: (1) B violated and only B paid; (2) A violated and only A paid; (3) B and C both violated, but only B paid and C was refunded while its VIOLATION remained stored; (4) earlier unavailable evidence blocked blame despite B's violation, then the deadline refunded all bonds with zero slash. "
        "Unlike role-assigned blame that charges contributors too, ordered local verdicts enforce one payer and an earlier-uncertainty barrier.\n"
        "Limits: synthetic bonds and fixture logs.")
    assert len(note) < 1000
    write('SUBMISSION_DRAFT.md', '# Owner-only Portal draft\n\nNot submitted. The contract repository remains PRIVATE.\n\n' + note + '\n\nCharacter count: ' + str(len(note)) + '.\n\nEvidence: [all four incidents](' + MANIFEST + '), [new contracts and key transactions](docs/LIVE_EXTENSIONS.md), [evidence inventory](docs/EVIDENCE.md).')
    print(json.dumps({'documentation_appended': True, 'portal_note_characters': len(note), 'portal_submitted': False}))


if __name__ == '__main__':
    main()
