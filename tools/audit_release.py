"""Independently audit the recorded release before its single private push."""
import hashlib
import json
import subprocess
from collections import Counter
from pathlib import Path

from live_release import accounting, normalized

ROOT = Path(__file__).resolve().parents[1]


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode('utf-8')).hexdigest()


def main():
    path = ROOT / 'deployments/studionet-release-2026-10-20.json'
    data = json.loads(path.read_text(encoding='utf-8'))
    if data.get('extension_runs'):
        original = json.loads(subprocess.run(['git', 'show', '87ab2d1ecf04c586527d36e297ca3d4bd9ec0356:deployments/studionet-release-2026-10-20.json'], cwd=ROOT, capture_output=True, check=True).stdout)
        for key, value in original.items():
            assert (data[key][:len(value)] if key in ('incidents', 'transactions', 'readbacks') else data[key]) == value, 'Historical field changed: ' + key
        data = original  # This auditor remains scoped to the preserved first release.
    assert data['status'] == 'LIVE_PASS'
    transactions = data['transactions']
    assert len(transactions) == 26 and len({t['hash'] for t in transactions}) == 26
    assert all(t['latest_status'] == 'FINALIZED' and t['finalized_observed'] for t in transactions)
    assert len([t for t in transactions if t['expected_error']]) == 8
    votes = {}
    for transaction in transactions:
        if transaction['expected_error']:
            assert transaction['leader_execution'] == 'ERROR' and transaction['leader_result_status'] == 'rollback'
            assert transaction['expected_error'] in str(transaction['leader_result_payload'])
        else:
            assert transaction['leader_execution'] == 'SUCCESS' and transaction['leader_result_status'] == 'return'
        assert transaction['validator_votes']
        votes[transaction['operation']] = dict(Counter(transaction['validator_votes'].values()))
    latest = {}
    by_name = {t['operation']: t for t in transactions}
    rejected_unchanged = []
    for reading in data['readbacks']:
        accounting(reading['state'], reading['accounting'])
        transaction = by_name.get(reading['after'])
        if transaction and transaction['expected_error']:
            assert normalized(reading['state']) == normalized(latest[reading['incident']])
            rejected_unchanged.append(transaction['operation'])
        latest[reading['incident']] = reading['state']
    assert len(data['readbacks']) == 28 and len(rejected_unchanged) == 8
    assert len({incident['address'].lower() for incident in data['incidents']}) == 2
    for incident in data['incidents']:
        assert incident['deployed_source_matches_git_blob'] and incident['deployed_source_sha256'] == data['source_sha256']
        final = latest[incident['id']]
        assert final['phase'] == 'SETTLED_FAULT' and final['settled'] and final['settlement_count'] == 1
        assert final['liable_index'] == incident['expected_liable_index']
        assert [row['effective_verdict'] for row in final['assessment']['steps']] == incident['expected_verdicts']
        for index, step in enumerate(final['config']['steps']):
            entry = final['ledger'][step['operator']]
            assert entry['slashed'] == (100 if index == final['liable_index'] else 0)
            assert entry['refunded'] == (0 if index == final['liable_index'] else 100)
        assert final['award_credit'] == {data['participants']['claimant']['address'].lower(): 100}
        reported = next(r['state'] for r in data['readbacks'] if r['after'] == incident['id'] + ':report')
        snapshot = {'schema_version': 'liability-cascade/1', 'contract_address': incident['address'].lower(),
                    'config': reported['config'], 'records': reported['records'],
                    'report': reported['report'], 'ledger': reported['ledger']}
        assert final['assessment']['snapshot_digest'] == digest(snapshot)
        receipt = dict(final['receipt'])
        receipt_hash = receipt.pop('receipt_digest')
        assert receipt_hash == digest(receipt)
        assert receipt['config_digest'] == digest(final['config'])
        assert receipt['assessment_digest'] == digest(final['assessment'])
        assert receipt['ledger'] == final['ledger'] and receipt['award_credit'] == final['award_credit']
        assert data['recording_deadline'] <= receipt['settled_at'] < data['adjudication_deadline']
        for row in final['assessment']['steps']:
            assert row['recorded'] and row['evidence_status'] == 'AVAILABLE' and row['basis'] == 'SEMANTIC'
            for side in ('input', 'output'):
                fixture = next(f for f in data['evidence']['fixtures'] if f['path'] == incident['id'] + '/' + row['step_id'] + '-' + side + '.txt')
                observation = row[side]
                assert observation['url'] == fixture['raw_url']
                assert observation['committed_digest'] == observation['observed_digest'] == fixture['sha256']
                assert observation['status'] == 'AVAILABLE' and observation['reason_code'] == 'OK'
                assert observation['http_status'] == 200 and observation['byte_length'] == fixture['byte_length']
    source = subprocess.run(['git', 'show', data['source_commit'] + ':' + data['source_path']], cwd=ROOT, check=True, capture_output=True).stdout
    assert source == (ROOT / data['source_path']).read_bytes()
    assert hashlib.sha256(source).hexdigest() == data['source_sha256']
    assert len(data['evidence']['fixtures']) == 12
    for fixture in data['evidence']['fixtures']:
        body = (ROOT / 'fixtures' / fixture['path']).read_bytes()
        assert len(body) == fixture['byte_length'] and hashlib.sha256(body).hexdigest() == fixture['sha256']
        assert b'\r' not in body and fixture['http_status'] == 200 and fixture['matches_local_bytes']
        assert '/' + data['evidence']['fixture_commit'] + '/' in fixture['raw_url']
    sensitive = []

    def scan(value, location='manifest'):
        if isinstance(value, dict):
            for key, child in value.items():
                name = key.lower().replace('-', '_')
                if name in {'private_key', 'privatekey', 'api_key', 'apikey', 'authorization', 'password', 'secret', 'secret_key', 'client_secret', 'bearer_token', 'signing_key', 'mnemonic', 'seed_phrase', 'access_token', 'refresh_token'} and child and child != '[REDACTED]':
                    sensitive.append(location + '.' + key)
                scan(child, location + '.' + key)
        elif isinstance(value, list):
            for index, child in enumerate(value):
                scan(child, location + '[' + str(index) + ']')

    scan(data)
    assert not sensitive, 'Sensitive field names require local redaction (values not displayed): ' + ','.join(sensitive)
    summary = {'status': 'PASS', 'source_commit': data['source_commit'], 'source_blob': data['source_blob'],
               'source_sha256': data['source_sha256'], 'transactions_finalized': 26, 'successful_executions': 18,
               'expected_rollbacks': 8, 'accepted_observed': sum(t['accepted_observed'] for t in transactions),
               'accounting_readbacks': 28, 'expected_reverts_preserved_state': rejected_unchanged,
               'snapshot_and_receipt_hashes_verified': 2, 'evidence_observations_verified': 12,
               'fixture_files_curl_measured': 12, 'fixture_total_bytes': sum(f['byte_length'] for f in data['evidence']['fixtures']),
               'vote_counts_by_operation': votes, 'sensitive_named_fields_found': 0,
               'gates': data['gates']}
    (ROOT / 'deployments/release-audit-2026-10-20.json').write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps({key: value for key, value in summary.items() if key not in ('expected_reverts_preserved_state', 'vote_counts_by_operation', 'gates')}))


if __name__ == '__main__':
    main()
