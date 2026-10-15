"""Compare the tool version each step asks for with the version that ran.

  python scripts/versions.py <workflow.ga> <planemo report.json>

Galaxy can run a different tool version than the workflow asks for, without an
error, for example when the requested version is not installed. The jobs pass,
but the results can differ. This check lists each difference as a warning.
It does not change pass or fail.

Steps are matched to jobs by step UUID, also inside subworkflows. Galaxy
built-in tools (no Tool Shed ID) record no version in the job, so they are
not compared.
"""
import json
import sys


def requested_tools(steps, out):
    for step in steps.values():
        if step.get("type") == "subworkflow":
            requested_tools(step["subworkflow"]["steps"], out)
        elif step.get("type") == "tool" and "/repos/" in (step.get("tool_id") or ""):
            out[step["uuid"]] = (step.get("label") or step.get("name"), step["tool_id"].rsplit("/", 1)[0], step["tool_version"])
    return out


def jobs_run(steps, out):
    for step in steps.values():
        if step.get("subworkflow"):
            jobs_run(step["subworkflow"].get("steps", {}), out)
        tool_ids = {job.get("tool_id") for job in step.get("jobs", []) if job.get("tool_id")}
        if tool_ids:
            out.setdefault(step.get("workflow_step_uuid"), set()).update(tool_ids)
    return out


def main(ga_path, report_path):
    try:
        workflow = json.load(open(ga_path))
        tests = json.load(open(report_path))["tests"]
    except (OSError, ValueError, KeyError) as e:
        print(f"Tool versions not compared: {e}")
        return
    asked = requested_tools(workflow["steps"], {})
    ran = {}
    for test in tests:
        jobs_run(test.get("data", {}).get("invocation_details", {}).get("steps", {}), ran)

    differences, compared = [], 0
    for uuid, (label, tool, version) in asked.items():
        for tool_id in sorted(ran.get(uuid, ())):
            compared += 1
            ran_tool, ran_version = tool_id.rsplit("/", 1) if "/repos/" in tool_id else (tool_id, "?")
            if ran_tool != tool or ran_version != version:
                differences.append((label, tool.split("/")[-1], version, ran_version if ran_tool == tool else tool_id))

    print(f"Tool versions: {compared} tool steps compared, {len(differences)} differ.")
    if differences:
        print()
        print("| Step | Tool | Workflow asks for | Galaxy ran |")
        print("|---|---|---|---|")
        for label, tool, version, ran_version in differences:
            print(f"| {label} | {tool} | {version} | {ran_version} |")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
