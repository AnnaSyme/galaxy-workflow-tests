"""Remove what one test run left in the Galaxy test account, if the run passed.

  python scripts/cleanup.py <planemo report.json> <run start, UTC ISO time>

Pass: purge the test history (purge, not delete: deleted datasets still count
against the quota) and delete the workflow copy that Planemo imported.
Fail or error: keep both, so the failed jobs can be inspected.

Safety: acts only on the IDs in this run's report. A history is purged only if
its name starts with "github-test: ". A workflow is deleted only if it was
created after this run started. The test data history never matches either rule.
"""
import json
import os
import sys
import urllib.request

GALAXY_URL = "https://usegalaxy.org.au"
HISTORY_PREFIX = "github-test: "


def api(method, path):
    req = urllib.request.Request(
        f"{GALAXY_URL}/api/{path}",
        method=method,
        headers={"x-api-key": os.environ["GALAXY_API_KEY"], "Accept": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        body = r.read().decode()
        return json.loads(body) if body else None


def main(report_path, run_started_at):
    try:
        tests = json.load(open(report_path))["tests"]
    except (OSError, ValueError, KeyError) as e:
        print(f"No usable report ({e}). Nothing removed.")
        return
    statuses = [t.get("data", {}).get("status") for t in tests]
    details = [t.get("data", {}).get("invocation_details", {}).get("details", {}) for t in tests]
    history_ids = {d["history_id"] for d in details if d.get("history_id")}
    workflow_ids = {d["workflow_id"] for d in details if d.get("workflow_id")}

    if not tests or any(s != "success" for s in statuses):
        print(f"Test status {statuses}: kept for inspection.")
        for h in sorted(history_ids):
            print(f"  history  {GALAXY_URL}/histories/view?id={h}")
        for w in sorted(workflow_ids):
            print(f"  workflow {w}")
        return

    for h in sorted(history_ids):
        name = api("GET", f"histories/{h}")["name"]
        if not name.startswith(HISTORY_PREFIX):
            print(f"Skipped history {h}: name {name!r} does not start with {HISTORY_PREFIX!r}")
            continue
        api("DELETE", f"histories/{h}?purge=true")
        print(f"Purged history {h} ({name})")

    for w in sorted(workflow_ids):
        created = api("GET", f"workflows/{w}").get("create_time", "")
        if created < run_started_at:
            print(f"Skipped workflow {w}: created {created}, before this run ({run_started_at})")
            continue
        api("DELETE", f"workflows/{w}")
        print(f"Deleted workflow copy {w} (created {created})")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
