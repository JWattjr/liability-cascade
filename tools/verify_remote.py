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
    fixture_commits = [data['evidence']['fixture_commit']]
    for extension in data.get('extension_runs', []):
        assert extension['status'] == 'LIVE_PASS'
        fixture_commit = extension['evidence']['fixture_commit']
        fixture_commits.append(fixture_commit)
        new_tree = json.loads(command(['gh', 'api', 'repos/JWattjr/genlayer-demo-evidence/git/trees/' + fixture_commit + '?recursive=1']))
        names = [item['path'] for item in new_tree['tree'] if item['type'] == 'blob']
        assert all(name.endswith('.txt') for name in names)
        assert len([name for name in names if name.startswith('liability-cascade/incident-3/')]) == 6
        assert len([name for name in names if name.startswith('liability-cascade/incident-4/')]) == 5
        assert 'liability-cascade/incident-4/A-input-missing.txt' not in names
    assert not command(['git', 'status', '--porcelain']).strip()
    proof = {'status': 'PASS', 'verified_at': datetime.now(timezone.utc).isoformat(),
             'repository': repository['html_url'], 'repository_visibility': 'PRIVATE',
             'local_and_remote_head': head, 'deployment_source_commit': data['source_commit'],
             'deployment_source_is_ancestor_and_present_remotely': True,
             'remote_source_git_blob': content['sha'], 'remote_source_sha256': hashlib.sha256(source).hexdigest(),
             'remote_source_matches_both_deployed_sources': all(i['deployed_source_matches_git_blob'] for i in data['incidents']),
             'public_fixture_commit': data['evidence']['fixture_commit'], 'public_tree_fixture_text_only': True,
             'liability_fixture_files': 12 + (11 if data.get('extension_runs') else 0),
             'public_fixture_commits': fixture_commits, 'deployed_source_count': len(data['incidents']),
             'remote_source_matches_all_deployed_sources': all(i['deployed_source_matches_git_blob'] for i in data['incidents']),
             'working_tree_clean': True, 'portal_submitted': False}
    output = ROOT / ('artifacts/remote-publication-verification-extension.json' if data.get('extension_runs') else 'artifacts/remote-publication-verification.json')
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(proof, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps(proof))


if __name__ == '__main__':
    main()
