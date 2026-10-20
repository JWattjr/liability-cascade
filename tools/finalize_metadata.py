import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

root = Path(__file__).resolve().parents[1]
path = root / 'deployments/studionet-release-2026-10-20.json'
data = json.loads(path.read_text(encoding='utf-8'))
assert data['status'] == 'LIVE_PASS'
verification = json.loads((root / 'verification/phase2-results.json').read_text(encoding='utf-8'))
assert verification['passed'] == 193 and verification['lint']['ok']
assert not any(verification['pytest'][field] for field in ('failures', 'errors', 'skipped'))


def command(args):
    return subprocess.run(args, cwd=root, capture_output=True, check=True, text=True).stdout.strip()


private_repo = json.loads(command(['gh', 'api', 'repos/JWattjr/liability-cascade']))
public_repo = json.loads(command(['gh', 'api', 'repos/JWattjr/genlayer-demo-evidence']))
assert private_repo['private'] is True and public_repo['private'] is False
data['repository'] = private_repo['html_url']
data['repository_visibility'] = 'PRIVATE'
data['repository_visibility_verified_at'] = datetime.now(timezone.utc).isoformat()
data['evidence_repository_visibility'] = 'PUBLIC'
data['local_verification'] = verification
data['final_regression_tests_sha256'] = hashlib.sha256((root / 'tests/test_cascade.py').read_bytes()).hexdigest()
data['final_regression_tests_git_blob'] = command(['git', 'hash-object', 'tests/test_cascade.py'])
data['toolchain'].update(python=sys.version.split()[0], runtime_executable=sys.executable,
    node=command(['node', '--version']), git=command(['git', '--version']),
    curl=command(['curl.exe', '--version']).splitlines()[0], gh=command(['gh', '--version']).splitlines()[0])
data['publication_provenance'] = {'deployment_source_commit': data['source_commit'],
    'final_documentation_commit_is_later': True,
    'required_remote_contract_blob': data['source_blob'],
    'required_remote_source_sha256': data['source_sha256'],
    'push_policy': 'One normal private contract-repository push after documentation and audit; report remote HEAD afterward.'}
path.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8', newline='\n')
print(json.dumps({'metadata_updated': True, 'contract_repository_visibility': 'PRIVATE', 'evidence_repository_visibility': 'PUBLIC', 'final_regression_tests_git_blob': data['final_regression_tests_git_blob']}))
