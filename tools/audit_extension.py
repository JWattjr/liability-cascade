"""Independent audit of the appended incidents and unchanged historical data."""
import hashlib
import json
import subprocess
from collections import Counter
from pathlib import Path

from audit_release import digest
from live_release import accounting, normalized

ROOT = Path(__file__).resolve().parents[1]
PATH = 'deployments/studionet-release-2026-10-20.json'
BASE = '87ab2d1ecf04c586527d36e297ca3d4bd9ec0356'


def main():
    data = json.loads((ROOT / PATH).read_text(encoding='utf-8'))
    baseline_bytes = subprocess.run(['git', 'show', BASE + ':' + PATH], cwd=ROOT, check=True, capture_output=True).stdout
    baseline = json.loads(baseline_bytes)
    for key, value in baseline.items():
        assert (data[key][:len(value)] if key in ('incidents', 'transactions', 'readbacks') else data[key]) == value, 'Historical entry changed: ' + key
    run = next(row for row in data['extension_runs'] if row['id'] == 'incidents-3-and-4')
    assert run['status'] == 'LIVE_PASS'
    assert run['baseline_manifest_sha256'] == hashlib.sha256(baseline_bytes).hexdigest()
    assert all(run['original_entry_digests'][key] == digest(baseline[key]) for key in ('incidents', 'transactions', 'readbacks'))
    assert len(data['incidents']) == 4 and len(data['transactions']) == 46 and len(data['readbacks']) == 50
    transactions, readings, incidents = data['transactions'][26:], data['readbacks'][28:], data['incidents'][2:]
    assert len({row['hash'] for row in data['transactions']}) == 46
    assert len({row['address'].lower() for row in data['incidents']}) == 4
    assert len(transactions) == 20 and len(readings) == 22
    assert all(row['latest_status'] == 'FINALIZED' and row['finalized_observed'] for row in transactions)
    assert sum(bool(row['expected_error']) for row in transactions) == 1
    by_name = {row['operation']: row for row in transactions}
    counts = {}
    for row in transactions:
        expected = row['expected_error']
        assert row['leader_execution'] == ('ERROR' if expected else 'SUCCESS')
        assert row['leader_result_status'] == ('rollback' if expected else 'return')
        if expected:
            assert row['operation'] == 'incident-4:early-timeout-rejected'
            assert expected == 'adjudication deadline not reached' and expected in row['leader_result_payload']
        assert row['validator_votes']
        counts[row['operation']] = dict(Counter(row['validator_votes'].values()))
    latest = {}
    for row in readings:
        accounting(row['state'], row['accounting'])
        transaction = by_name.get(row['after'])
        if transaction and transaction['expected_error']:
            assert normalized(row['state']) == normalized(latest[row['incident']])
        latest[row['incident']] = row['state']
    summary_incidents = []
    for incident in incidents:
        identity = incident['id']
        assert incident['source_commit'] == data['source_commit'] == 'da39762abefd3027ab72d47821c06313db1e1993'
        assert incident['deployed_source_matches_git_blob'] and incident['deployed_source_sha256'] == data['source_sha256']
        state = latest[identity]
        expected = ['FAITHFUL', 'VIOLATION', 'VIOLATION'] if identity == 'incident-3' else ['UNCLEAR', 'VIOLATION', 'FAITHFUL']
        assert [row['effective_verdict'] for row in state['assessment']['steps']] == expected
        assert state['settled'] and state['settlement_count'] == 1 and state['assessment_count'] == 1
        assert state['phase'] == ('SETTLED_FAULT' if identity == 'incident-3' else 'SETTLED_UNATTRIBUTABLE')
        assert state['outcome'] == ('PIPELINE_FAULT' if identity == 'incident-3' else 'UNATTRIBUTABLE')
        assert state['liable_index'] == (1 if identity == 'incident-3' else None)
        assert len(state['records']) == 3 and state['report']['claimant'] == data['participants']['claimant']['address'].lower()
        assert state['report']['claimant'] not in state['ledger']
        reported = next(row['state'] for row in readings if row['after'] == identity + ':report')
        snapshot = {'schema_version': 'liability-cascade/1', 'contract_address': incident['address'].lower(), 'config': reported['config'],
                    'records': reported['records'], 'report': reported['report'], 'ledger': reported['ledger']}
        assert state['assessment']['snapshot_digest'] == digest(snapshot)
        for step in state['assessment']['steps']:
            assert step['recorded']
            for side in ('input', 'output'):
                measured = next(f for f in run['evidence']['fixtures'] if f['incident'] == identity and f['step_id'] == step['step_id'] and f['side'] == side)
                observation = step[side]
                assert observation['url'] == measured['raw_url'] and observation['committed_digest'] == measured['sha256']
                assert observation['http_status'] == measured['http_status'] and observation['byte_length'] == measured['byte_length']
                if measured['http_status'] == 404:
                    assert observation['status'] == 'UNAVAILABLE' and observation['reason_code'] == 'HTTP_STATUS' and observation['observed_digest'] is None
                    assert step['evidence_status'] == 'UNAVAILABLE' and step['basis'] == 'UNAVAILABLE_LOG' and step['semantic_verdict'] == 'NOT_EVALUATED'
                else:
                    assert observation['status'] == 'AVAILABLE' and observation['reason_code'] == 'OK' and observation['observed_digest'] == measured['sha256']
                    body = (ROOT / 'fixtures' / measured['path']).read_bytes()
                    assert b'\r' not in body and body.endswith(b'\n') and hashlib.sha256(body).hexdigest() == measured['sha256']
            if not (identity == 'incident-4' and step['step_id'] == 'A'):
                assert step['evidence_status'] == 'AVAILABLE' and step['basis'] == 'SEMANTIC'
                assert step['semantic_verdict'] == expected[step['index']]
        for index, step in enumerate(state['config']['steps']):
            row = state['ledger'][step['operator']]
            liable = identity == 'incident-3' and index == 1
            assert row['deposited'] == 100 and row['slashed'] == (100 if liable else 0) and row['refunded'] == (0 if liable else 100)
            assert row['available'] == row['locked'] == 0
        assert state['award_credit'] == ({state['report']['claimant']: 100} if identity == 'incident-3' else {})
        receipt = dict(state['receipt'])
        assert receipt.pop('receipt_digest') == digest(receipt)
        assert receipt['config_digest'] == digest(state['config']) and receipt['assessment_digest'] == digest(state['assessment'])
        assert receipt['ledger'] == state['ledger'] and receipt['award_credit'] == state['award_credit']
        assert all(row['recorded_at'] < incident['recording_deadline'] for row in state['records'].values())
        assert incident['recording_deadline'] <= state['report']['reported_at'] < incident['adjudication_deadline']
        if identity == 'incident-3':
            assert receipt['settled_at'] < incident['adjudication_deadline']
        else:
            awaiting = next(row for row in readings if row['after'] == 'incident-4:adjudicate')
            assert awaiting['state']['phase'] == 'AWAITING_REFUND' and not awaiting['state']['settled']
            assert awaiting['accounting']['totals']['locked'] == 300 and awaiting['accounting']['totals']['slashed'] == awaiting['accounting']['totals']['refunded'] == 0
            assert state['assessment'] == awaiting['state']['assessment']
            assert receipt['settled_at'] >= incident['adjudication_deadline']
        summary_incidents.append({'id': identity, 'address': incident['address'], 'verdicts': expected, 'outcome': state['outcome'],
            'phase': state['phase'], 'ledger': state['ledger'], 'award_credit': state['award_credit'], 'snapshot_and_receipt_hashes_verified': True})
    source = subprocess.run(['git', 'show', data['source_commit'] + ':' + data['source_path']], cwd=ROOT, capture_output=True, check=True).stdout
    assert source == (ROOT / data['source_path']).read_bytes() and hashlib.sha256(source).hexdigest() == data['source_sha256']
    sensitive = []
    def scan(value, location='manifest'):
        if isinstance(value, dict):
            for key, child in value.items():
                if key.lower().replace('-', '_') in {'private_key', 'privatekey', 'api_key', 'apikey', 'authorization', 'password', 'secret', 'secret_key', 'client_secret', 'bearer_token', 'signing_key', 'mnemonic', 'seed_phrase', 'access_token', 'refresh_token'} and child and child != '[REDACTED]':
                    sensitive.append(location + '.' + key)
                scan(child, location + '.' + key)
        elif isinstance(value, list):
            for index, child in enumerate(value):
                scan(child, location + '[' + str(index) + ']')
    scan(data)
    assert not sensitive, 'Sensitive field names found; values not displayed: ' + ','.join(sensitive)
    result = {'status': 'PASS', 'source_commit': data['source_commit'], 'source_blob': data['source_blob'], 'source_sha256': data['source_sha256'],
        'original_manifest_entries_unchanged': True, 'original_counts': run['original_entry_counts'],
        'new_finalized_transactions': 20, 'new_successful_executions': 19, 'new_expected_rollbacks': 1,
        'new_accepted_observed': sum(row['accepted_observed'] for row in transactions), 'new_state_accounting_readbacks': 22,
        'combined_finalized_transactions': 46, 'combined_readbacks': 50, 'combined_deployments': 4,
        'fixture_commit': run['evidence']['fixture_commit'], 'published_new_lf_logs': 11, 'missing_404_references': 1,
        'votes_by_operation': counts, 'incidents': summary_incidents, 'sensitive_named_fields_found': 0}
    (ROOT / 'deployments/extension-audit-2026-10-20.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps({key: value for key, value in result.items() if key not in ('votes_by_operation', 'incidents')}))


if __name__ == '__main__':
    main()
