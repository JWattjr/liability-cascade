"""Reproduce Phase 2 verification using the owner's fixed existing venv."""

import ast
import hashlib
import importlib.metadata
import json
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VENV = Path("C:/Users/User/Desktop/Genlayer apps/intelligent-contracts-v2/.venv")
EXPECTED_HEADER = '# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }'
OUT = ROOT / "verification"


def write(name, value):
    (OUT / name).write_text(value.replace("\r\n", "\n"), encoding="utf-8", newline="\n")


def run(name, args):
    process = subprocess.run(args, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
    write(name + ".stdout.txt", process.stdout)
    write(name + ".stderr.txt", process.stderr)
    if process.returncode:
        print(process.stdout)
        print(process.stderr)
        raise SystemExit(process.returncode)
    return process.stdout


def main():
    if Path(sys.executable).resolve() != (VENV / "Scripts/python.exe").resolve():
        raise SystemExit("Use the pinned existing venv interpreter")
    OUT.mkdir(exist_ok=True)
    lint = json.loads(run("lint", [str(VENV / "Scripts/genvm-lint.exe"), "check", "contracts/liability_cascade.py", "--json"]))
    if not lint.get("ok"):
        raise SystemExit("Contract lint failed")
    schema = json.loads(run("schema", [str(VENV / "Scripts/genvm-lint.exe"), "schema", "contracts/liability_cascade.py", "--json"]))
    write("schema.json", json.dumps(schema, indent=2) + "\n")
    run("pytest", [sys.executable, "-m", "pytest", "--junitxml=verification/pytest.xml"])
    tree = ET.parse(OUT / "pytest.xml").getroot()
    suites = [tree] if tree.tag == "testsuite" else list(tree.iter("testsuite"))
    counts = {key: sum(int(s.get(key, "0")) for s in suites) for key in ("tests", "failures", "errors", "skipped")}
    if any(counts[k] for k in ("failures", "errors", "skipped")):
        raise SystemExit("All direct tests must pass without skips")
    source = (ROOT / "contracts/liability_cascade.py").read_bytes()
    assert source.decode().splitlines()[0] == EXPECTED_HEADER
    assert (ROOT / ".gitattributes").read_text() == "* text=auto eol=lf\n"
    files = []
    for relative in [".gitattributes", ".gitignore", "pytest.ini", "gltest.config.yaml", "README.md"]:
        files.append(ROOT / relative)
    for directory in ("contracts", "tests", "tools", "docs", "verification"):
        files.extend(p for p in (ROOT / directory).rglob("*") if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc")
    for path in files:
        body = path.read_bytes()
        assert b"\r" not in body, "Non-LF content: " + str(path)
        body.decode("utf-8")
    parsed = ast.parse(source)
    cls = next(n for n in parsed.body if isinstance(n, ast.ClassDef) and n.name == "LiabilityCascade")
    public = {n.name for n in cls.body if isinstance(n, ast.FunctionDef) and any(ast.unparse(d).startswith("gl.public.") for d in n.decorator_list)}
    assert public == set(schema["schema"]["methods"])
    result = {"phase": 2, "status": "PASS", "python": sys.version.split()[0], "interpreter": str(Path(sys.executable)),
              "packages": {p: importlib.metadata.version(p) for p in ("genlayer-py", "genlayer-test", "genvm-linter", "pytest")},
              "source_sha256": hashlib.sha256(source).hexdigest(), "lint": lint, "pytest": counts,
              "passed": counts["tests"], "public_methods": len(public), "lf_files_checked": len(files),
              "scope": "Local direct VM and captured validators only; no network consensus, keys, deployment or push."}
    write("phase2-results.json", json.dumps(result, indent=2) + "\n")
    print(json.dumps({"status": "PASS", "passed": counts["tests"], "lint_ast_checks": lint["lint"]["passed"],
                      "sdk_validation": lint["validate"]["ok"], "public_methods": len(public), "source_sha256": result["source_sha256"]}))


if __name__ == "__main__":
    main()
