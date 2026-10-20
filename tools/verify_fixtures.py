"""Measure commit-pinned public fixture response bodies using curl."""
import argparse
import hashlib
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--commit', required=True)
    args = parser.parse_args()
    if not re.fullmatch(r'[0-9a-f]{40}', args.commit):
        raise SystemExit('Exact fixture commit SHA required')
    rows = []
    for local in sorted((ROOT / 'fixtures').glob('incident-*/*.txt')):
        relative = local.relative_to(ROOT / 'fixtures').as_posix()
        url = f'https://raw.githubusercontent.com/JWattjr/genlayer-demo-evidence/{args.commit}/liability-cascade/{relative}'
        fetched = ROOT / 'artifacts' / 'raw-fixtures' / relative
        fetched.parent.mkdir(parents=True, exist_ok=True)
        command = ['curl.exe', '--silent', '--show-error', '--fail', '--proto', '=https',
                   '--connect-timeout', '10', '--max-time', '45', '--max-redirs', '0',
                   '--output', str(fetched), '--write-out', '%{http_code}', url]
        process = subprocess.run(command, capture_output=True, text=True, timeout=50)
        if process.returncode or process.stdout != '200':
            raise RuntimeError(f'Fixture fetch failed for {relative}: HTTP {process.stdout}, curl {process.returncode}')
        body = fetched.read_bytes()
        body.decode('utf-8', errors='strict')
        if not (body == local.read_bytes() and b'\r' not in body and body.endswith(b'\n') and 0 < len(body) <= 15000):
            raise RuntimeError('Fixture byte/encoding/size mismatch: ' + relative)
        rows.append({'path': relative, 'raw_url': url, 'http_status': 200, 'byte_length': len(body),
                     'sha256': hashlib.sha256(body).hexdigest(), 'matches_local_bytes': True, 'line_endings': 'LF'})
    if len(rows) != 12:
        raise RuntimeError('Expected exactly twelve measured pipeline artifacts')
    result = {'repository': 'https://github.com/JWattjr/genlayer-demo-evidence', 'visibility': 'PUBLIC',
              'fixture_commit': args.commit, 'folder': 'liability-cascade',
              'measured_at': datetime.now(timezone.utc).isoformat(), 'measurement_tool': 'curl.exe',
              'redirects_followed': False, 'fixtures': rows}
    (ROOT / 'fixtures' / 'evidence-manifest.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps({'fixture_commit': args.commit, 'curl_verified_files': len(rows), 'bytes': sum(r['byte_length'] for r in rows)}))


if __name__ == '__main__':
    main()
