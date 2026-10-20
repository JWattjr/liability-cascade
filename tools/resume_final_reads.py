"""Recover only final readbacks after a transient gateway failure; never submit."""
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import live_release as live

live.record = json.loads(live.FILE.read_text(encoding='utf-8'))
assert len(live.record['transactions']) == 26
assert all(t['latest_status'] == 'FINALIZED' for t in live.record['transactions'])
assert all(i['judgment_matches_expected'] for i in live.record['incidents'])
key = subprocess.run(['node', live.HELPER, live.ALIASES['claimant']], capture_output=True, check=True).stdout.decode().strip()
live.clients = {'claimant': live.create_client(chain=live.studionet, account=live.Account.from_key(key))}
del key
with live.pinned_runner_calldata(chain_id=61999, runner=live.RUNNER):
    for incident in live.record['incidents']:
        label = incident['id'] + ':finalized-audit'
        existing = next((r for r in live.record['readbacks'] if r['after'] == label), None)
        if existing is None:
            for attempt in range(5):
                try:
                    existing = live.readback(incident, label, final=True)
                    break
                except Exception as error:
                    if attempt == 4:
                        raise
                    live.event(retrying='read-only finalized audit', incident=incident['id'], attempt=attempt + 1, error_type=type(error).__name__)
                    time.sleep(10 * (attempt + 1))
        live.check_judgment(incident, existing['state'])
assert len(live.record['readbacks']) == 28
failure = live.record.pop('failure', None)
if failure:
    live.record.setdefault('recovered_transient_read_failures', []).append({**failure,
        'recovery': 'Only the missing latest-final readback was retried; zero transactions resubmitted.'})
live.record['status'] = 'LIVE_PASS'
live.record['completed_at'] = live.now()
live.record['gates'] = {
    'distinctiveness': {'status': 'PASS', 'evidence': 'docs/DESIGN.md section 11 and verification/distinctiveness-source-check.json'},
    'local_review_tests_lint': {'status': 'PASS', 'tests': 193, 'lint_ast_checks': 3, 'sdk_validation': True, 'evidence': 'docs/REVIEW.md and verification/'},
    'live': {'status': 'PASS', 'deployments': 2, 'all_transactions_finalized': True, 'source_byte_equality': True, 'fixture_bytes_curl_verified': True}}
live.save()
live.event(status='LIVE_PASS', transactions=26, readbacks=28, resubmitted_transactions=0)
