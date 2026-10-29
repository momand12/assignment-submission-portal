"""Convert pytest's JUnit XML results into our JSON test report.

Usage:  python ci/make_report.py results.xml test-report.json

Run information (repository, branch, commit, run id, run number) comes from
the environment variables that GitHub Actions sets automatically.
"""
import json
import os
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone


def read_tests(xml_path):
    """Return a list of {name, result, failure_message} from the JUnit XML file."""
    tests = []
    if not os.path.exists(xml_path):
        # pytest did not even run (for example the install step failed)
        return tests

    root = ET.parse(xml_path).getroot()
    for case in root.iter("testcase"):
        result = "passed"
        message = None
        for tag in ("failure", "error", "skipped"):
            element = case.find(tag)
            if element is not None:
                result = "skipped" if tag == "skipped" else "failed"
                message = element.get("message") or (element.text or "").strip()
                break
        tests.append({
            "name": case.get("name"),
            "result": result,
            "failure_message": message if result == "failed" else None,
        })
    return tests


def make_report(xml_path):
    tests = read_tests(xml_path)
    passed = sum(1 for t in tests if t["result"] == "passed")
    failed = sum(1 for t in tests if t["result"] == "failed")
    return {
        "repository": os.environ.get("GITHUB_REPOSITORY", "local"),
        "branch": os.environ.get("GITHUB_REF_NAME", "local"),
        "commit_sha": os.environ.get("GITHUB_SHA", "local"),
        "run_id": os.environ.get("GITHUB_RUN_ID", "local"),
        "run_number": os.environ.get("GITHUB_RUN_NUMBER", "local"),
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "tests": tests,
        "total": len(tests),
        "passed": passed,
        "failed": failed,
        # No tests at all also counts as failed, because nothing was proven.
        "overall_status": "passed" if tests and failed == 0 else "failed",
    }


if __name__ == "__main__":
    xml_file = sys.argv[1] if len(sys.argv) > 1 else "results.xml"
    out_file = sys.argv[2] if len(sys.argv) > 2 else "test-report.json"
    report = make_report(xml_file)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"Wrote {out_file}: {report['overall_status'].upper()} "
          f"({report['passed']} passed, {report['failed']} failed, {report['total']} total)")
