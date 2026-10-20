"""Read-only publication proof; writes only an ignored local audit artifact."""
import base64
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def command(args):
    return subprocess.run(args, cwd=ROOT, check=True, capture_output=True).stdout


def main():
    data = json.loads((ROOT / 'deployments/studionet-release-2026-10-20.json').read_text(encoding='utf-8'))
    assert data['status'] == 'LIVE_PASS'
    head = command(['git', 'rev-parse', 'HEAD']).decode().strip()
    remote = command(['git', 'ls-remote', 'origin', 'refs/heads/main']).decode().split()[0]
    assert remote == head
    command(['git', 'merge-base', '--is-ancestor', data['source_commit'], head])
    repository = json.loads(command(['gh', 'api', 'repos/JWattjr/liability-cascade']))
    assert repository['private'] is True
    content = json.loads(command(['gh', 'api', 'repos/JWattjr/liability-cascade/contents/' + data['source_path'] + '?ref=' + head]))
    source = base64.b64decode(content['content'])
    assert content['sha'] == data['source_blob']
    assert source == command(['git', 'show', data['source_commit'] + ':' + data['source_path']])
    assert source == (ROOT / data['source_path']).read_bytes()
    assert hashlib.sha256(source).hexdigest() == data['source_sha256']
    original = json.loads(command(['gh', 'api', 'repos/JWattjr/liability-cascade/commits/' + data['source_commit']]))
    assert original['sha'] == data['source_commit']
    evidence_repo = json.loads(command(['gh', 'api', 'repos/JWattjr/genlayer-demo-evidence']))
    assert evidence_repo['private'] is False
    tree = json.loads(command(['gh', 'api', 'repos/JWattjr/genlayer-demo-evidence/git/trees/' + data['evidence']['fixture_commit'] + '?recursive=1']))
    files = [item['path'] for item in tree['tree'] if item['type'] == 'blob']
    assert all(path.endswith('.txt') for path in files)
    assert len([path for path in files if path.startswith('liability-cascade/')]) == 12
    assert not command(['git', 'status', '--porcelain']).strip()
    proof = {'status': 'PASS', 'verified_at': datetime.now(timezone.utc).isoformat(),
             'repository': repository['html_url'], 'repository_visibility': 'PRIVATE',
             'local_and_remote_head': head, 'deployment_source_commit': data['source_commit'],
             'deployment_source_is_ancestor_and_present_remotely': True,
             'remote_source_git_blob': content['sha'], 'remote_source_sha256': hashlib.sha256(source).hexdigest(),
             'remote_source_matches_both_deployed_sources': all(i['deployed_source_matches_git_blob'] for i in data['incidents']),
             'public_fixture_commit': data['evidence']['fixture_commit'], 'public_tree_fixture_text_only': True,
             'liability_fixture_files': 12, 'working_tree_clean': True, 'portal_submitted': False}
    output = ROOT / 'artifacts/remote-publication-verification.json'
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(proof, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps(proof))


if __name__ == '__main__':
    main()
