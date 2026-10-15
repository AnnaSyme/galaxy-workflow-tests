"""Open, update and close one GitHub issue per failing workflow.

  python scripts/issues.py <outcome.json> <repo> [--dry-run]

A failing workflow gets an open issue titled "Test failing: <name>". If that
issue is already open, the script adds a comment instead of a second issue.
When the workflow passes again, the script comments on the issue and closes it.
So the open issues are always the current failures. Needs the gh CLI and a
token that can write issues (GH_TOKEN).
"""
import json
import subprocess
import sys

DRY = "--dry-run" in sys.argv


def gh(*args):
    if DRY and args[1] in ("create", "comment", "close"):
        print("DRY RUN: gh", " ".join(args[:3]), "...")
        return ""
    return subprocess.run(["gh", *args], check=True, capture_output=True, text=True).stdout


def open_issue(repo, name):
    found = json.loads(gh("issue", "list", "--repo", repo, "--state", "open", "--search", f'"Test failing: {name}" in:title',
                          "--json", "number,title"))
    return next((i["number"] for i in found if i["title"] == f"Test failing: {name}"), None)


def body(row):
    version = f"{row['source']} {row['id']} version {row['version']}" if row["version"] else "unknown (download may have failed)"
    return (f"**{row['title'] or row['name']}** failed its test on {row['date']}.\n\n"
            f"- Result: {row['result']}\n- Version tested: {version}\n- Run: {row['run_url']}\n\n"
            f"Problem reported by Planemo:\n\n```\n{row['problem'] or 'none recorded'}\n```\n\n"
            "The test history is kept in the gtntesting account for inspection. "
            "This issue closes itself when the workflow passes again.")


def main(path, repo):
    outcome = json.load(open(path))
    for row in outcome["failed"]:
        number = open_issue(repo, row["name"])
        if number:
            gh("issue", "comment", str(number), "--repo", repo, "--body", body(row))
            print(f"Commented on issue #{number}: {row['name']}")
        else:
            gh("issue", "create", "--repo", repo, "--title", f"Test failing: {row['name']}", "--body", body(row))
            print(f"Opened issue: {row['name']}")
    for row in outcome["passed"]:
        number = open_issue(repo, row["name"])
        if number:
            gh("issue", "comment", str(number), "--repo", repo, "--body", f"Passed again on {row['date']}: {row['run_url']}")
            gh("issue", "close", str(number), "--repo", repo)
            print(f"Closed issue #{number}: {row['name']}")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--dry-run"]
    if len(args) != 2:
        sys.exit(__doc__)
    main(*args)
