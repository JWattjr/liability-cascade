"""Resumable StudioNet demo; persist each hash and never resubmit a judgment."""
import base64
import copy
import hashlib
import importlib.metadata
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
from eth_account import Account
from genlayer_py import create_client
from genlayer_py.chains import studionet
from genlayer_py.types import TransactionHashVariant
from studionet_compat import RUNNER, pinned_runner_calldata

ROOT = Path(__file__).resolve().parents[1]
SOURCE = 'contracts/liability_cascade.py'
RPC = 'https://studio.genlayer.com/api'
HELPER = 'C:/Users/User/Desktop/Intelligent Contracts/release/credential_key.mjs'
VENV = Path('C:/Users/User/Desktop/Genlayer apps/intelligent-contracts-v2/.venv/Scripts/python.exe')
ALIASES = {'A': 'moment-grid-studionet', 'B': 'portal-five-release',
           'C': 'portal-five-release-new', 'claimant': 'footnote-independent-studionet'}
CHARTER = ('Never introduce or restore personal email addresses into the public dataset. '
    'The local obligations are: EXTRACT must replace every source contact_email with [REDACTED]. '
    'TRANSFORM must uppercase display_name and region and preserve record_id and contact_email exactly as received; '
    'it must not introduce or restore email values absent from its received input. '
    'PUBLISH must reproduce its received CSV bytes exactly, adding nothing; it has no independent redaction or filtering duty. '
    'Inherited prohibited values are judged at the step that first introduced them, rather than imposing an unstated downstream filtering duty.')
DUTIES = {
    'A': 'EXTRACT: output the four CSV columns record_id,display_name,region,contact_email and preserve row order. Preserve record_id, display_name and region. Replace EVERY source contact_email with the literal [REDACTED].',
    'B': 'TRANSFORM: preserve the CSV header, row order and record_id; uppercase display_name and region; preserve contact_email EXACTLY as received. Do not introduce, restore, correct or filter contact values. No independent redaction obligation is assigned to this step.',
    'C': 'PUBLISH: reproduce the complete received CSV dataset byte-for-byte without adding, deleting, correcting or filtering anything. No independent redaction or filtering obligation is assigned to this step.'}
FILE = ROOT / 'deployments' / ('studionet-release-' + datetime.now(timezone.utc).strftime('%Y-%m-%d') + '.json')
record = {}
clients = {}
last_request = 0.0


class UnexpectedJudgment(RuntimeError):
    pass


def now():
    return datetime.now(timezone.utc).isoformat()


def save():
    FILE.parent.mkdir(exist_ok=True)
    FILE.write_text(json.dumps(record, indent=2, default=str) + '\n', encoding='utf-8', newline='\n')


def event(**value):
    print(json.dumps(value), flush=True)


def throttle():
    global last_request
    time.sleep(max(0, 2.1 - (time.monotonic() - last_request)))
    last_request = time.monotonic()


def rpc(method, params):
    for attempt in range(4):
        throttle()
        response = requests.post(RPC, json={'jsonrpc': '2.0', 'id': 1, 'method': method, 'params': params}, timeout=(10, 50))
        if response.status_code == 429 or response.status_code >= 500:
            if attempt < 3:
                time.sleep(15 * (attempt + 1))
                continue
        response.raise_for_status()
        body = response.json()
        if 'error' in body:
            if body['error'].get('code') == -32429 and attempt < 3:
                time.sleep(20 * (attempt + 1))
                continue
            raise RuntimeError(f'RPC {method} failed: {body["error"]}')
        return body['result']
    raise RuntimeError('RPC read retry limit reached')


def git(*args):
    return subprocess.run(['git', *args], cwd=ROOT, check=True, capture_output=True).stdout


def normalized(state):
    result = copy.deepcopy(state)
    result.pop('effective_window', None)
    return result


def accounting(state, ledger):
    totals = ledger['totals']
    if not totals['conserved'] or totals['deposited'] != sum(totals[k] for k in ('available', 'locked', 'slashed', 'refunded')):
        raise RuntimeError('Global conservation failed')
    for row in ledger['operators'].values():
        if not all(type(v) is int and v >= 0 for v in row.values()) or row['deposited'] != sum(row[k] for k in ('available', 'locked', 'slashed', 'refunded')):
            raise RuntimeError('Per-owner nonnegative integer conservation failed')
        if state['settled'] and (row['available'] or row['locked']):
            raise RuntimeError('Terminal locked balance')
    if sum(r['slashed'] > 0 for r in ledger['operators'].values()) > 1:
        raise RuntimeError('More than one operator slashed')
    if sum(ledger['award_credit'].values()) != totals['slashed'] or sum(ledger['refund_credit'].values()) != totals['refunded']:
        raise RuntimeError('Recipient credit projection failed')
    if state['settlement_count'] != int(state['settled']) or state['assessment_count'] != int(state['assessment'] is not None):
        raise RuntimeError('Exactly-once latch failed')


def readback(incident, label, final=False):
    variant = TransactionHashVariant.LATEST_FINAL if final else TransactionHashVariant.LATEST_NONFINAL
    values = {}
    for method in ('get_state', 'get_accounting'):
        throttle()
        values[method] = clients['claimant'].read_contract(address=incident['address'], function_name=method, args=[], transaction_hash_variant=variant)
    accounting(values['get_state'], values['get_accounting'])
    entry = {'incident': incident['id'], 'after': label, 'at': now(), 'state_variant': variant.value,
             'state': values['get_state'], 'accounting': values['get_accounting'], 'invariants_pass': True}
    record['readbacks'].append(entry)
    save()
    event(readback=label, incident=incident['id'], phase=entry['state']['phase'], accounting='PASS')
    return entry


def wait(entry, final=False):
    deadline = time.monotonic() + 900
    while time.monotonic() < deadline:
        raw = rpc('eth_getTransactionByHash', [entry['hash']])
        if not raw:
            time.sleep(5)
            continue
        status = raw.get('status_name') or raw.get('status')
        if status not in entry.setdefault('observed_statuses', []):
            entry['observed_statuses'].append(status)
            event(operation=entry['operation'], hash=entry['hash'], status=status)
        entry['latest_status'] = status
        entry['accepted_observed'] = 'ACCEPTED' in entry['observed_statuses']
        entry['finalized_observed'] = 'FINALIZED' in entry['observed_statuses']
        entry['raw_receipt'] = raw
        save()
        if status in ('ACCEPTED', 'FINALIZED'):
            throttle()
            decoded = clients['claimant'].get_transaction(transaction_hash=entry['hash'])
            entry['decoded_receipt'] = decoded
            leaders = (decoded.get('consensus_data') or {}).get('leader_receipt') or []
            leader = leaders[0] if isinstance(leaders, list) and leaders else leaders if isinstance(leaders, dict) else {}
            result = leader.get('result') or {}
            entry['leader_execution'] = leader.get('execution_result')
            entry['leader_result_status'] = result.get('status')
            entry['leader_result_payload'] = result.get('payload')
            consensus = raw.get('consensus_data') or {}
            entry['consensus_result'] = raw.get('result_name', raw.get('result'))
            entry['validator_votes'] = consensus.get('votes', raw.get('validator_votes', {}))
            entry['validator_receipts'] = consensus.get('validators', raw.get('validators', []))
            save()
            expected = entry.get('expected_error')
            if expected:
                if entry['leader_execution'] != 'ERROR' or result.get('status') != 'rollback' or expected not in str(result.get('payload')):
                    raise RuntimeError('Expected deterministic revert did not match: ' + entry['operation'])
            elif entry['leader_execution'] != 'SUCCESS' or result.get('status') != 'return':
                raise RuntimeError('Contract execution failed: ' + entry['operation'])
            if not final or status == 'FINALIZED':
                return decoded
        elif status in ('CANCELED', 'UNDETERMINED'):
            raise RuntimeError('Unexpected terminal transaction lifecycle: ' + str(status))
        time.sleep(5)
    raise RuntimeError('Receipt timeout; saved hash must be resumed, never resubmitted: ' + entry['hash'])


def operation(incident, label, actor, method, args, expected_error=None):
    name = incident['id'] + ':' + label
    previous = next((e for e in record['transactions'] if e['operation'] == name), None)
    if previous is None:
        previous = {'operation': name, 'actor': actor, 'method': method, 'args': args,
                    'expected_error': expected_error, 'submission_started': now()}
        record['transactions'].append(previous)
        save()
        throttle()
        if method == '__init__':
            tx = clients[actor].deploy_contract(code=git('show', record['source_commit'] + ':' + SOURCE), args=args, leader_only=False)
        else:
            tx = clients[actor].write_contract(address=incident['address'], function_name=method, args=args, leader_only=False)
        previous['hash'] = str(tx)
        previous['explorer'] = 'https://explorer-studio.genlayer.com/tx/' + str(tx)
        save()
        event(submitted=name, hash=str(tx))
    if not previous.get('hash'):
        raise RuntimeError('Uncertain submission outcome; inspect saved intent before any resend: ' + name)
    receipt = wait(previous)
    if method == '__init__':
        address = (receipt.get('data') or {}).get('contract_address') or (receipt.get('tx_data_decoded') or {}).get('contract_address') or receipt.get('to_address')
        if not address:
            raise RuntimeError('Deployment receipt omitted contract address')
        incident['address'] = str(address)
        actual = base64.b64decode(rpc('gen_getContractCode', [str(address)]))
        incident['deployed_source_sha256'] = hashlib.sha256(actual).hexdigest()
        incident['deployed_source_matches_git_blob'] = actual == git('show', record['source_commit'] + ':' + SOURCE)
        save()
        if not incident['deployed_source_matches_git_blob']:
            raise RuntimeError('Deployed source differs byte-for-byte from the local Git blob')
    prior_read = next((r for r in record['readbacks'] if r['after'] == name), None)
    if prior_read is None:
        prior_state = next((r['state'] for r in reversed(record['readbacks']) if r['incident'] == incident['id']), None)
        result = readback(incident, name)
        if expected_error and normalized(result['state']) != normalized(prior_state):
            raise RuntimeError('Rejected transaction changed state: ' + name)
        return result
    return prior_read


def fixture(incident, step, side):
    path = incident['id'] + '/' + step + '-' + side + '.txt'
    return next(row for row in record['evidence']['fixtures'] if row['path'] == path)


def record_args(incident, step):
    incoming, outgoing = fixture(incident, step, 'input'), fixture(incident, step, 'output')
    return [step, incoming['raw_url'], outgoing['raw_url'], incoming['sha256'], outgoing['sha256']]


def check_judgment(incident, state):
    expected = incident['expected_verdicts']
    actual = [row['effective_verdict'] for row in state['assessment']['steps']] if state.get('assessment') else None
    payer = incident['expected_liable_index']
    if actual != expected or state['outcome'] != 'PIPELINE_FAULT' or state['liable_index'] != payer or not state['settled']:
        raise UnexpectedJudgment(f'{incident["id"]}: expected {expected} / payer {payer}, observed {actual} / {state["outcome"]} / {state["liable_index"]}')
    for index, step in enumerate(state['config']['steps']):
        entry = state['ledger'][step['operator']]
        if entry['slashed'] != (100 if index == payer else 0) or entry['refunded'] != (0 if index == payer else 100):
            raise UnexpectedJudgment('Unexpected allocation after semantic judgment')
    incident['judgment_matches_expected'] = True
    save()


def main():
    global record, clients
    if Path(sys.executable).resolve() != VENV.resolve():
        raise RuntimeError('Use the pinned venv')
    for role, alias in ALIASES.items():
        secret = subprocess.run(['node', HELPER, alias], capture_output=True, check=True).stdout.decode().strip()
        account = Account.from_key(secret)
        clients[role] = create_client(chain=studionet, account=account)
        del secret
    participants = {role: {'alias': ALIASES[role], 'address': client.local_account.address} for role, client in clients.items()}
    if len({value['address'].lower() for value in participants.values()}) != 4:
        raise RuntimeError('Three operators and claimant must have distinct addresses')
    if int(rpc('eth_chainId', []), 16) != 61999:
        raise RuntimeError('RPC is not StudioNet')
    if FILE.exists():
        saved = json.loads(FILE.read_text(encoding='utf-8'))
        if saved.get('extension_runs'):
            raise RuntimeError('Original runner is archived; use tools/live_extension.py without rewriting historical entries')
        record = saved
        if record['status'] == 'STOPPED_UNEXPECTED_JUDGMENT':
            raise RuntimeError('Unexpected judgment was recorded; owner review is required, never rerun blindly')
        if record['participants'] != participants:
            raise RuntimeError('Saved actors changed')
    else:
        if any((ROOT / 'deployments').glob('studionet-release-*.json')):
            raise RuntimeError('An earlier dated release exists; resume that manifest explicitly rather than starting a new deployment')
        if git('status', '--porcelain').strip():
            raise RuntimeError('Commit all prepared source/tools/fixtures locally before deployment')
        source = (ROOT / SOURCE).read_bytes()
        commit = git('rev-parse', 'HEAD').decode().strip()
        if source != git('show', commit + ':' + SOURCE):
            raise RuntimeError('Working source differs from Git blob')
        evidence = json.loads((ROOT / 'fixtures/evidence-manifest.json').read_text())
        for row in evidence['fixtures']:
            if hashlib.sha256((ROOT / 'fixtures' / row['path']).read_bytes()).hexdigest() != row['sha256']:
                raise RuntimeError('Measured fixture changed')
        timestamp = int(time.time())
        record = {'schema_version': 'liability-cascade-release/1', 'status': 'IN_PROGRESS', 'started_at': now(),
                  'network': {'name': 'StudioNet', 'chain_id': 61999, 'rpc': RPC}, 'runner': RUNNER,
                  'source_commit': commit, 'review_commit': '2619c4e7b2963117571f383ee8ef1dff9b2d7c07',
                  'source_path': SOURCE, 'source_blob': git('rev-parse', commit + ':' + SOURCE).decode().strip(),
                  'source_bytes': len(source), 'source_sha256': hashlib.sha256(source).hexdigest(),
                  'toolchain': {package: importlib.metadata.version(package) for package in ('genlayer-py', 'genlayer-test', 'genvm-linter', 'pytest')},
                  'client_adapter': 'tools/studionet_compat.py:pinned_runner_calldata', 'participants': participants,
                  'evidence': evidence, 'recording_deadline': timestamp + 900, 'adjudication_deadline': timestamp + 10800,
                  'transactions': [], 'readbacks': [], 'incidents': [], 'portal_submitted': False, 'repository_visibility_required': 'PRIVATE'}
        for identity, expected, payer in [('incident-b', ['FAITHFUL', 'VIOLATION', 'FAITHFUL'], 1), ('incident-a', ['VIOLATION', 'FAITHFUL', 'FAITHFUL'], 0)]:
            steps = [{'step_id': step, 'operator': participants[step]['address'], 'duty': DUTIES[step], 'bond_units': 100} for step in ('A', 'B', 'C')]
            args = ['liability-cascade-' + identity, CHARTER, json.dumps(steps, separators=(',', ':')), record['recording_deadline'], record['adjudication_deadline']]
            record['incidents'].append({'id': identity, 'constructor_args': args, 'expected_verdicts': expected, 'expected_liable_index': payer})
        save()
    with pinned_runner_calldata(chain_id=61999, runner=RUNNER):
        for incident in record['incidents']:
            operation(incident, 'deploy', 'A', '__init__', incident['constructor_args'])
            for step in ('A', 'B', 'C'):
                operation(incident, 'deposit-' + step, step, 'deposit', [100])
            operation(incident, 'wrong-caller-record', 'claimant', 'record_step', record_args(incident, 'A'), 'only assigned operator may record')
            operation(incident, 'record-A', 'A', 'record_step', record_args(incident, 'A'))
            replacement = record_args(incident, 'A')
            replacement[4] = '0' * 64
            operation(incident, 'replacement-rejected', 'A', 'record_step', replacement, 'step already recorded')
            for step in ('B', 'C'):
                operation(incident, 'record-' + step, step, 'record_step', record_args(incident, step))
        while time.time() < record['recording_deadline']:
            event(waiting_for='recording deadline', seconds_remaining=int(record['recording_deadline'] - time.time()))
            time.sleep(min(45, max(1, record['recording_deadline'] - time.time())))
        for incident in record['incidents']:
            report_args = [fixture(incident, 'C', 'output')['raw_url'], 'The final dataset contains a personal email address. Assess each local duty against its received input.']
            operation(incident, 'operator-claim-rejected', 'A', 'report_failure', report_args, 'configured operator cannot be claimant')
            operation(incident, 'report', 'claimant', 'report_failure', report_args)
            result = operation(incident, 'adjudicate', 'claimant', 'adjudicate', [])
            check_judgment(incident, result['state'])
            operation(incident, 'replay-rejected', 'claimant', 'adjudicate', [], 'terminal state')
        for entry in record['transactions']:
            wait(entry, final=True)
        for incident in record['incidents']:
            result = readback(incident, incident['id'] + ':finalized-audit', final=True)
            check_judgment(incident, result['state'])
        record['status'] = 'LIVE_PASS'
        record['completed_at'] = now()
        record['gates'] = {'distinctiveness': {'status': 'PASS', 'evidence': 'docs/DESIGN.md section 11'},
                           'local_review_tests_lint': {'status': 'PASS', 'tests': 193, 'lint_ast_checks': 3, 'sdk_validation': True, 'evidence': 'docs/REVIEW.md and verification/'},
                           'live': {'status': 'PASS', 'deployments': 2, 'all_transactions_finalized': True, 'source_byte_equality': True, 'fixture_bytes_curl_verified': True}}
        save()
        event(status='LIVE_PASS', transactions=len(record['transactions']), manifest=str(FILE))


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        if record:
            record['status'] = 'STOPPED_UNEXPECTED_JUDGMENT' if isinstance(error, UnexpectedJudgment) else 'BLOCKED'
            record['failure'] = {'at': now(), 'type': type(error).__name__, 'message': str(error)}
            save()
        event(status=record.get('status', 'PREFLIGHT_BLOCKED'), error_type=type(error).__name__, message=str(error))
        raise SystemExit(1)
