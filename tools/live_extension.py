"""Append incidents 3/4; immutable source and historical-entry preservation."""
import copy
import hashlib
import json
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import live_release as live

ROOT = Path(__file__).resolve().parents[1]
SOURCE_COMMIT = 'da39762abefd3027ab72d47821c06313db1e1993'
BASELINE_COMMIT = '87ab2d1ecf04c586527d36e297ca3d4bd9ec0356'
MANIFEST = 'deployments/studionet-release-2026-10-20.json'
RUN_ID = 'incidents-3-and-4'
baseline = {}
run = {}


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True)


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def preserve_history():
    for key, original in baseline.items():
        if key in ('incidents', 'transactions', 'readbacks'):
            if live.record[key][:len(original)] != original:
                raise RuntimeError('Historical manifest entries changed: ' + key)
        elif live.record[key] != original:
            raise RuntimeError('Historical manifest field changed: ' + key)


def save():
    preserve_history()
    temporary = live.FILE.with_suffix('.json.tmp')
    temporary.write_text(json.dumps(live.record, indent=2) + '\n', encoding='utf-8', newline='\n')
    temporary.replace(live.FILE)


def transient(error):
    message = str(error).lower()
    return any(word in message for word in ('502', '503', '504', '429', 'timed out', 'connection reset', 'invalid json'))


def retry_reads(function):
    def wrapped(*args, **kwargs):
        for attempt in range(4):
            try:
                return function(*args, **kwargs)
            except Exception as error:
                if not transient(error) or attempt == 3:
                    raise
                run.setdefault('transient_read_recoveries', []).append({'at': live.now(), 'function': function.__name__, 'error_type': type(error).__name__, 'attempt': attempt + 1})
                save()
                live.event(retry='read-only, same saved hash', function=function.__name__, attempt=attempt + 1)
                time.sleep(5 * (attempt + 1))
    return wrapped


def fixture(identity, step, side):
    return next(row for row in run['evidence']['fixtures'] if row['incident'] == identity and row['step_id'] == step and row['side'] == side)


def args_for(incident, step):
    incoming, outgoing = fixture(incident['id'], step, 'input'), fixture(incident['id'], step, 'output')
    return [step, incoming['raw_url'], outgoing['raw_url'], incoming['sha256'], outgoing['sha256']]


def expect(condition, message, reading):
    if not condition:
        run['unexpected_readback'] = reading
        save()
        raise live.UnexpectedJudgment(message)


def check(incident, reading, terminal=False):
    state, ledger = reading['state'], reading['accounting']
    assessment = state.get('assessment')
    expected = incident['expected_verdicts']
    actual = [row['effective_verdict'] for row in assessment['steps']] if assessment else None
    expect(actual == expected, 'Unexpected per-step verdicts: ' + incident['id'] + ' ' + str(actual), reading)
    expect(state['assessment_count'] == 1, 'Assessment count changed', reading)
    for index, row in enumerate(assessment['steps']):
        unavailable = incident['id'] == 'incident-4' and index == 0
        if unavailable:
            expect(row['evidence_status'] == 'UNAVAILABLE' and row['semantic_verdict'] == 'NOT_EVALUATED' and row['basis'] == 'UNAVAILABLE_LOG', 'A must be unavailable, not a semantic judgment', reading)
            expect(row['input']['status'] == 'UNAVAILABLE' and row['input']['http_status'] == 404 and row['input']['observed_digest'] is None, 'Missing A input must be a 404 observation', reading)
        else:
            expect(row['evidence_status'] == 'AVAILABLE' and row['basis'] == 'SEMANTIC' and row['semantic_verdict'] == expected[index], 'Expected available semantic verdict', reading)
    totals = ledger['totals']
    expect(totals['deposited'] == 300 and totals['available'] == 0, 'Unexpected funding totals', reading)
    if incident['id'] == 'incident-3':
        expect(state['outcome'] == 'PIPELINE_FAULT' and state['phase'] == 'SETTLED_FAULT' and state['liable_index'] == 1 and state['settled'], 'Only B must be liable despite C violation', reading)
        expect(totals['slashed'] == 100 and totals['refunded'] == 200 and totals['locked'] == 0 and state['settlement_count'] == 1, 'Wrong incident 3 totals', reading)
        for index, step in enumerate(state['config']['steps']):
            entry = state['ledger'][step['operator']]
            expect(entry['slashed'] == (100 if index == 1 else 0) and entry['refunded'] == (0 if index == 1 else 100), 'Wrong earliest-only allocation', reading)
    else:
        expect(state['outcome'] == 'UNATTRIBUTABLE' and state['liable_index'] is None and totals['slashed'] == 0 and not state['award_credit'], 'Uncertainty must block all blame', reading)
        expect(state['phase'] == ('SETTLED_UNATTRIBUTABLE' if terminal else 'AWAITING_REFUND') and state['settled'] == terminal, 'Wrong uncertainty phase', reading)
        expect(totals['locked'] == (0 if terminal else 300) and totals['refunded'] == (300 if terminal else 0) and state['settlement_count'] == int(terminal), 'Wrong uncertainty ledger movement', reading)
        if terminal:
            expect(digest(assessment) == incident['frozen_assessment_digest'], 'Deadline refund rewrote assessment', reading)
            expect(all(entry['refunded'] == 100 for entry in state['ledger'].values()), 'Every bond must be refunded', reading)
    incident['judgment_matches_expected'] = True
    if incident['id'] == 'incident-4' and not terminal:
        incident['frozen_assessment_digest'] = digest(assessment)
    save()


def sleep_until(deadline, label):
    while time.time() < deadline:
        live.event(waiting_for=label, seconds_remaining=int(deadline - time.time()))
        time.sleep(min(30, max(1, deadline - time.time())))


def main():
    global baseline, run
    if Path(sys.executable).resolve() != live.VENV.resolve():
        raise RuntimeError('Use pinned existing venv')
    live.FILE = ROOT / MANIFEST
    baseline_bytes = live.git('show', BASELINE_COMMIT + ':' + MANIFEST)
    baseline = json.loads(baseline_bytes)
    live.record = json.loads(live.FILE.read_text(encoding='utf-8'))
    preserve_history()
    source = live.git('show', SOURCE_COMMIT + ':' + live.SOURCE)
    if live.record['source_commit'] != SOURCE_COMMIT or source != (ROOT / live.SOURCE).read_bytes():
        raise RuntimeError('Source must remain the exact da39762 blob')
    existing = next((item for item in live.record.get('extension_runs', []) if item['id'] == RUN_ID), None)
    if existing:
        run = existing
        if run['status'] == 'STOPPED_UNEXPECTED_JUDGMENT':
            live.event(extension_status=run['status'], message='Unexpected judgment already recorded; never retry')
            raise SystemExit(1)
        if run['status'] == 'LIVE_PASS':
            live.event(extension_status='LIVE_PASS', message='Already complete; no transaction or historical entry touched')
            return
    else:
        evidence = json.loads((ROOT / 'fixtures/evidence-extension-2026-10-20.json').read_text(encoding='utf-8'))
        run = {'id': RUN_ID, 'status': 'IN_PROGRESS', 'started_at': live.now(), 'source_commit': SOURCE_COMMIT,
               'source_blob': live.record['source_blob'], 'source_sha256': hashlib.sha256(source).hexdigest(),
               'tooling_commit': live.git('rev-parse', 'HEAD').decode().strip(), 'evidence': evidence,
               'baseline_release_commit': BASELINE_COMMIT, 'baseline_manifest_sha256': hashlib.sha256(baseline_bytes).hexdigest(),
               'original_entry_counts': {'incidents': 2, 'transactions': 26, 'readbacks': 28},
               'original_entry_digests': {key: digest(baseline[key]) for key in ('incidents', 'transactions', 'readbacks')},
               'deadline_policy_seconds': {'recording_from_deployment_preparation': 240, 'adjudication_after_recording': 240}}
        live.record.setdefault('extension_runs', []).append(run)
    live.save = save
    live.readback = retry_reads(live.readback)
    live.wait = retry_reads(live.wait)
    save()
    for role, alias in live.ALIASES.items():
        key = subprocess.run(['node', live.HELPER, alias], check=True, capture_output=True).stdout.decode().strip()
        live.clients[role] = live.create_client(chain=live.studionet, account=live.Account.from_key(key))
        del key
        if live.clients[role].local_account.address.lower() != baseline['participants'][role]['address'].lower():
            raise RuntimeError('Existing participant changed')
    if len({client.local_account.address.lower() for client in live.clients.values()}) != 4:
        raise RuntimeError('Claimant must be separate from all operators')
    if int(live.rpc('eth_chainId', []), 16) != 61999:
        raise RuntimeError('Not StudioNet')
    with live.pinned_runner_calldata(chain_id=61999, runner=live.RUNNER):
        for identity, expected, payer in [('incident-3', ['FAITHFUL', 'VIOLATION', 'VIOLATION'], 1), ('incident-4', ['UNCLEAR', 'VIOLATION', 'FAITHFUL'], None)]:
            incident = next((row for row in live.record['incidents'] if row['id'] == identity), None)
            if incident is None:
                timestamp = int(time.time())
                recording, adjudication = timestamp + 240, timestamp + 480
                steps = [{'step_id': step, 'operator': baseline['participants'][step]['address'], 'duty': live.DUTIES[step], 'bond_units': 100} for step in ('A', 'B', 'C')]
                constructor = ['liability-cascade-' + identity, live.CHARTER, json.dumps(steps, separators=(',', ':')), recording, adjudication]
                incident = {'id': identity, 'extension_run': RUN_ID, 'constructor_args': constructor, 'recording_deadline': recording,
                            'adjudication_deadline': adjudication, 'expected_verdicts': expected, 'expected_liable_index': payer,
                            'expected_outcome': 'PIPELINE_FAULT' if payer is not None else 'UNATTRIBUTABLE', 'source_commit': SOURCE_COMMIT}
                live.record['incidents'].append(incident)
                save()
                live.event(incident=identity, recording_closes_lagos=datetime.fromtimestamp(recording, timezone(timedelta(hours=1))).isoformat(), adjudication_closes_lagos=datetime.fromtimestamp(adjudication, timezone(timedelta(hours=1))).isoformat())
            live.operation(incident, 'deploy', 'A', '__init__', incident['constructor_args'])
            for step in ('A', 'B', 'C'):
                live.operation(incident, 'deposit-' + step, step, 'deposit', [100])
            for step in ('A', 'B', 'C'):
                live.operation(incident, 'record-' + step, step, 'record_step', args_for(incident, step))
        for identity in ('incident-3', 'incident-4'):
            incident = next(row for row in live.record['incidents'] if row['id'] == identity)
            sleep_until(incident['recording_deadline'] + 1, identity + ' recording deadline')
            report = [fixture(identity, 'C', 'output')['raw_url'], 'The final dataset contains personal email addresses. Assess each local duty using its received input.']
            live.operation(incident, 'report', 'claimant', 'report_failure', report)
            reading = live.operation(incident, 'adjudicate', 'claimant', 'adjudicate', [])
            check(incident, reading)
            if identity == 'incident-4':
                if not any(t['operation'] == identity + ':early-timeout-rejected' for t in live.record['transactions']) and time.time() >= incident['adjudication_deadline'] - 30:
                    raise RuntimeError('Insufficient time remains to demonstrate an early timeout revert safely')
                reading = live.operation(incident, 'early-timeout-rejected', 'claimant', 'settle_deadline', [], 'adjudication deadline not reached')
                check(incident, reading)
                sleep_until(incident['adjudication_deadline'] + 1, identity + ' adjudication deadline')
                reading = live.operation(incident, 'deadline-refund', 'claimant', 'settle_deadline', [])
                check(incident, reading, terminal=True)
        for transaction in live.record['transactions'][26:]:
            live.wait(transaction, final=True)
        for incident in live.record['incidents'][2:]:
            label = incident['id'] + ':finalized-audit'
            reading = next((r for r in live.record['readbacks'][28:] if r['after'] == label), None)
            if reading is None:
                reading = live.readback(incident, label, final=True)
            check(incident, reading, terminal=incident['id'] == 'incident-4')
        run.update(status='LIVE_PASS', completed_at=live.now(), new_transactions=20, new_readbacks=22,
                   historical_entries_unchanged=True, contract_source_unchanged=True)
        save()
        live.event(extension_status='LIVE_PASS', new_transactions=20, new_readbacks=22, historical_entries_unchanged=True)


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        if run:
            run['status'] = 'STOPPED_UNEXPECTED_JUDGMENT' if isinstance(error, live.UnexpectedJudgment) else 'BLOCKED'
            run['failure'] = {'at': live.now(), 'type': type(error).__name__, 'message': str(error)}
            save()
        live.event(extension_status=run.get('status', 'PREFLIGHT_BLOCKED'), error_type=type(error).__name__, message=str(error))
        if isinstance(error, live.UnexpectedJudgment):
            live.event(full_readback=run.get('unexpected_readback'))
        raise SystemExit(1)
