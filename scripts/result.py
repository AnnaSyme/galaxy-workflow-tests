"""Decide pass or fail from a Planemo JSON report.

  python scripts/result.py <report.json> <copy for HTML.json>

Exit 0 if every test case has status "success", else 1. A missing or unreadable
report is a fail. Planemo's own exit code is not used: it is also non-zero when
only the HTML report fails to render.

Also writes a copy of the report with null job_metrics replaced by [], so that
"planemo test_reports" can build the HTML report. Galaxy Australia returns null
job_metrics, and the Planemo 0.75.35 HTML template fails on null.
"""
import json
import sys


def main(report_path, html_copy_path):
    try:
        report = json.load(open(report_path))
        tests = report["tests"]
    except (OSError, ValueError, KeyError) as e:
        print(f"FAIL: no usable Planemo report ({e})")
        return 1
    for test in tests:
        steps = test.get("data", {}).get("invocation_details", {}).get("steps", {})
        for step in steps.values():
            for job in step.get("jobs", []):
                if job.get("job_metrics") is None:
                    job["job_metrics"] = []
    json.dump(report, open(html_copy_path, "w"))

    statuses = [(t.get("id"), t.get("data", {}).get("status")) for t in tests]
    for test_id, status in statuses:
        print(f"{status}: {test_id}")
    if tests and all(s == "success" for _, s in statuses):
        print("PASS")
        return 0
    print("FAIL")
    return 1


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    sys.exit(main(sys.argv[1], sys.argv[2]))
