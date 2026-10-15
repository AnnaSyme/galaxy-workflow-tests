"""Record the results of one Action run.

  python scripts/record.py <names JSON> <reports dir> <run URL> <run number> <date>

Appends one line per tested workflow to results/history.csv, rebuilds
RESULTS.md from the full history, and writes outcome.json (passes and
failures of this run) for scripts/issues.py.

<reports dir> holds the downloaded artifacts: <dir>/report-<name>/<name>.json,
<name>.source.json and <name>.versions.md. A workflow with no report is
recorded as "error".
"""
import csv
import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
HISTORY = ROOT / "results" / "history.csv"
TABLE = ROOT / "RESULTS.md"
FIELDS = ["date", "run", "name", "title", "source", "id", "version", "result", "version_warnings", "run_url", "problem"]


def read_json(path):
    try:
        return json.load(open(path))
    except (OSError, ValueError):
        return None


def outcome_for(name, reports_dir):
    folder = Path(reports_dir) / f"report-{name}"
    report = read_json(folder / f"{name}.json")
    source = read_json(folder / f"{name}.source.json") or {}
    row = {"name": name, "title": source.get("title", ""), "source": source.get("source", ""),
           "id": source.get("id", ""), "version": source.get("version", ""), "version_warnings": "", "problem": ""}
    if report is None or not report.get("tests"):
        row.update(result="error", problem="No Planemo report. See the run log.")
        return row
    statuses = [t.get("data", {}).get("status") for t in report["tests"]]
    row["result"] = "pass" if all(s == "success" for s in statuses) else "fail"
    if row["result"] == "fail":
        problems = []
        for t in report["tests"]:
            data = t.get("data", {})
            if data.get("status") == "success":
                continue
            if data.get("execution_problem"):
                problems.append(str(data["execution_problem"]))
            problems.extend(str(p) for p in data.get("output_problems") or [])
        row["problem"] = " | ".join(problems)[:1500] or "Test status: " + ", ".join(map(str, statuses))
    versions = folder / f"{name}.versions.md"
    if versions.exists():
        m = re.search(r"(\d+) differ", versions.read_text())
        row["version_warnings"] = m.group(1) if m else ""
    return row


def load_history():
    if not HISTORY.exists():
        return []
    return list(csv.DictReader(open(HISTORY, newline="")))


def write_table(history):
    manifest = yaml.safe_load((ROOT / "workflows.yml").read_text())
    lines = [
        "**Test results**",
        "",
        "Latest result of each workflow. Made by the Action from `results/history.csv`, which keeps every run.",
        "",
        "| Workflow | Last result | Last tested | Last passed | Version tested | Version warnings | Run |",
        "|---|---|---|---|---|---|---|",
    ]
    for entry in manifest:
        rows = [r for r in history if r["name"] == entry["name"]]
        if not rows:
            lines.append(f"| {entry['title']} | not tested yet | | | | | |")
            continue
        last = rows[-1]
        passed = [r["date"] for r in rows if r["result"] == "pass"]
        version = f"{last['source']} {last['id']} v{last['version']}" if last["version"] else ""
        lines.append(f"| {entry['title']} | {last['result']} | {last['date']} | {passed[-1] if passed else 'never'} "
                     f"| {version} | {last['version_warnings']} | [run {last['run']}]({last['run_url']}) |")
    TABLE.write_text("\n".join(lines) + "\n")


def main(names_json, reports_dir, run_url, run_number, date):
    names = json.loads(names_json)
    new_rows = []
    for name in names:
        row = outcome_for(name, reports_dir)
        row.update(date=date, run=str(run_number), run_url=run_url)
        new_rows.append(row)
    HISTORY.parent.mkdir(exist_ok=True)
    is_new = not HISTORY.exists()
    with open(HISTORY, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        if is_new:
            writer.writeheader()
        writer.writerows(new_rows)
    write_table(load_history())
    outcome = {"passed": [r for r in new_rows if r["result"] == "pass"],
               "failed": [r for r in new_rows if r["result"] != "pass"]}
    Path("outcome.json").write_text(json.dumps(outcome, indent=2))
    for r in new_rows:
        print(f"{r['result']}: {r['name']} (version {r['version'] or '?'}, version warnings {r['version_warnings'] or '-'})")


if __name__ == "__main__":
    if len(sys.argv) != 6:
        sys.exit(__doc__)
    main(*sys.argv[1:])
