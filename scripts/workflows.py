"""Read workflows.yml, and download a workflow from its source.

  python scripts/workflows.py list [all | name,name,...]   JSON list of names, for the Action matrix
  python scripts/workflows.py fetch <name> <out_dir>       write <name>.ga and <name>-tests.yml to out_dir

Downloads use no API key, so a workflow that is not public fails here.
"""
import hashlib
import json
import shutil
import sys
import urllib.request
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
GALAXY_URL = "https://usegalaxy.org.au"
TRS_URL = "https://workflowhub.eu/ga4gh/trs/v2/tools"


def load_manifest():
    entries = yaml.safe_load((ROOT / "workflows.yml").read_text())
    names = [e["name"] for e in entries]
    if len(names) != len(set(names)):
        sys.exit("workflows.yml: duplicate name")
    return {e["name"]: e for e in entries}


def get(url):
    req = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "galaxy-workflow-tests"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode()


def fetch_galaxy(entry):
    url = f"{GALAXY_URL}/api/workflows/{entry['id']}/download?format=json-download"
    if str(entry["version"]) != "latest":
        url += f"&version={entry['version']}"
    return get(url), str(entry["version"]), url


def fetch_workflowhub(entry):
    version = str(entry["version"])
    if version == "latest":
        versions = json.loads(get(f"{TRS_URL}/{entry['id']}/versions"))
        version = str(max(int(v["id"]) for v in versions))
    url = f"{TRS_URL}/{entry['id']}/versions/{version}/GALAXY/descriptor"
    return json.loads(get(url))["content"], version, url


def cmd_list(selection):
    manifest = load_manifest()
    if selection in ("", "all"):
        names = list(manifest)
    else:
        names = [n.strip() for n in selection.split(",") if n.strip()]
        unknown = [n for n in names if n not in manifest]
        if unknown:
            sys.exit(f"Not in workflows.yml: {', '.join(unknown)}")
    print(json.dumps(names))


def cmd_fetch(name, out_dir):
    entry = load_manifest()[name]
    test_file = ROOT / "tests" / f"{name}-tests.yml"
    if not test_file.exists():
        sys.exit(f"Missing test file: {test_file}")
    fetchers = {"galaxy": fetch_galaxy, "workflowhub": fetch_workflowhub}
    content, version, url = fetchers[entry["source"]](entry)
    workflow = json.loads(content)
    if workflow.get("a_galaxy_workflow") != "true":
        sys.exit(f"Not a Galaxy workflow: {url}")
    if version == "latest" and "version" in workflow:
        version = str(workflow["version"])
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / f"{name}.ga").write_text(content)
    shutil.copy(test_file, out / f"{name}-tests.yml")
    info = {
        "name": name,
        "title": workflow.get("name"),
        "source": entry["source"],
        "id": str(entry["id"]),
        "version": version,
        "url": url,
        "sha256": hashlib.sha256(content.encode()).hexdigest(),
    }
    (out / f"{name}.source.json").write_text(json.dumps(info, indent=2) + "\n")
    print(json.dumps(info, indent=2))


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "list":
        cmd_list(sys.argv[2] if len(sys.argv) > 2 else "all")
    elif len(sys.argv) == 4 and sys.argv[1] == "fetch":
        cmd_fetch(sys.argv[2], sys.argv[3])
    else:
        sys.exit(__doc__)
