"""Measure new LF fixtures and the deliberately missing input with curl."""
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
    commit = parser.parse_args().commit
    assert re.fullmatch('[0-9a-f]{40}', commit)
    rows = []
    for identity in ('incident-3', 'incident-4'):
        for step in ('A', 'B', 'C'):
            for side in ('input', 'output'):
                missing = identity == 'incident-4' and step == 'A' and side == 'input'
                name = 'A-input-missing.txt' if missing else step + '-' + side + '.txt'
                relative = identity + '/' + name
                url = f'https://raw.githubusercontent.com/JWattjr/genlayer-demo-evidence/{commit}/liability-cascade/{relative}'
                target = ROOT / 'artifacts/extension-curl' / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                hashes = []
                for sample in range(2 if missing else 1):
                    process = subprocess.run(['curl.exe', '--silent', '--show-error', '--proto', '=https',
                        '--connect-timeout', '10', '--max-time', '45', '--max-redirs', '0',
                        '--output', str(target), '--write-out', '%{http_code}', url], capture_output=True, text=True, timeout=50)
                    status = 404 if missing else 200
                    assert process.returncode == 0 and process.stdout == str(status), 'Unexpected curl status for ' + relative
                    body = target.read_bytes()
                    body.decode('utf-8', errors='strict')
                    hashes.append(hashlib.sha256(body).hexdigest())
                assert len(set(hashes)) == 1
                if not missing:
                    assert body == (ROOT / 'fixtures' / relative).read_bytes()
                    assert b'\r' not in body and body.endswith(b'\n') and 0 < len(body) <= 15000
                rows.append({'incident': identity, 'step_id': step, 'side': side, 'path': relative,
                    'raw_url': url, 'http_status': status, 'byte_length': len(body), 'sha256': hashes[0],
                    'kind': 'INTENTIONALLY_MISSING_INPUT' if missing else 'PUBLISHED_LOG',
                    'line_endings': 'LF' if not missing else ('LF' if body.endswith(b'\n') else 'SERVER_404_BODY_WITHOUT_TRAILING_LF'),
                    'curl_samples': len(hashes), 'digest_source': 'Exact complete curl response-body bytes, without normalization',
                    'matches_local_fixture': None if missing else True})
    manifest = {'fixture_commit': commit, 'repository': 'https://github.com/JWattjr/genlayer-demo-evidence',
                'visibility': 'PUBLIC', 'measured_at': datetime.now(timezone.utc).isoformat(),
                'measurement_tool': 'curl.exe', 'redirects_followed': False, 'fixtures': rows,
                'missing_input_note': 'The pinned A input path is absent. Its committed digest is the hash of the exact measured 404 body; that server error body is not an eligible LF step log. HTTP 404 makes it UNAVAILABLE before integrity/semantic checks.'}
    (ROOT / 'fixtures/evidence-extension-2026-10-20.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps({'fixture_commit': commit, 'published_lf_logs': 11, 'intentionally_missing_404': 1,
        'served_body_bytes_total': sum(row['byte_length'] for row in rows), 'missing_digest': next(row['sha256'] for row in rows if row['kind'] == 'INTENTIONALLY_MISSING_INPUT')}))


if __name__ == '__main__':
    main()
