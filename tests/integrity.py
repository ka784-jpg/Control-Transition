"""Check preserved assets, relative documentation links, and executable plots."""
import csv
import hashlib
import json
import math
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import tomllib
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]


def main():
    manifest = json.loads((ROOT / "docs" / "manifest.json").read_text())
    for item in manifest["files"]:
        assert hashlib.sha256((ROOT / item["path"]).read_bytes()).hexdigest() == item["sha256"]
    classical = tomllib.loads((ROOT / "examples/expected/classical/metadata.toml").read_text())
    assert classical["source_sha256"] == manifest["files"][0]["sha256"]
    quantum = json.loads((ROOT / "examples/expected/qiskit/metadata.json").read_text())
    assert quantum["source_sha256"] == hashlib.sha256((ROOT / "examples/qiskit_local.py").read_bytes()).hexdigest()
    links = 0
    files = [ROOT / "README.md", ROOT / "CONTRIBUTING.md", *(ROOT / "docs").rglob("*.md")]
    for path in files:
        for target in re.findall(r"\]\(([^)]+)\)", path.read_text()):
            if urlsplit(target).scheme or target.startswith("#"):
                continue
            assert (path.parent / unquote(target.split("#", 1)[0])).exists(), (path, target)
            links += 1
    for path in (ROOT / "examples" / "expected").rglob("*.csv"):
        with path.open(newline="") as stream:
            rows = list(csv.DictReader(stream))
        assert rows and all(math.isfinite(float(v)) for row in rows for v in row.values())
    if "--plots" in sys.argv:
        with tempfile.TemporaryDirectory() as directory:
            for model in ("classical", "qiskit"):
                output = Path(directory) / (model + ".png")
                command = [sys.executable, str(ROOT / "examples" / "plot.py"),
                           str(ROOT / "examples" / "expected" / model), str(output)]
                subprocess.run(command, check=True)
                before = output.read_bytes()
                assert before.startswith(b"\x89PNG\r\n\x1a\n")
                assert subprocess.run(command, capture_output=True).returncode != 0
                assert output.read_bytes() == before
    print(f"Verified {len(manifest['files'])} hashes, {links} local links, and example data.")


if __name__ == "__main__":
    main()
