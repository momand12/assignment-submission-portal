"""Email the JSON test report (Bonus 2).

Usage:  python ci/send_email.py test-report.json

All settings come from environment variables, which the workflow fills from
GitHub secrets and variables. Nothing secret is written in this file.
  SMTP_USERNAME    sender Gmail address          (secret)
  SMTP_PASSWORD    Gmail app password            (secret)
  REPORT_EMAIL_TO  address that gets the report  (repository variable)
  SMTP_SERVER      default smtp.gmail.com
  SMTP_PORT        default 587
"""
import json
import os
import smtplib
import sys
from email.message import EmailMessage


def build_email(report, report_text, sender, receiver):
    status = report["overall_status"].upper()
    short_sha = report["commit_sha"][:7]

    lines = [
        f"Repository:  {report['repository']}",
        f"Branch:      {report['branch']}",
        f"Commit SHA:  {report['commit_sha']}",
        f"Run:         #{report['run_number']} (id {report['run_id']})",
        f"Time (UTC):  {report['timestamp']}",
        f"Result:      {status}",
        f"Tests:       {report['total']} total, {report['passed']} passed, {report['failed']} failed",
        "",
        "Each test:",
    ]
    for test in report["tests"]:
        line = f"  [{test['result'].upper()}] {test['name']}"
        if test["failure_message"]:
            line += f"\n      -> {test['failure_message']}"
        lines.append(line)
    lines += ["", "Full JSON report:", report_text]

    msg = EmailMessage()
    msg["Subject"] = f"[{status}] CI report - {short_sha}"
    msg["From"] = sender
    msg["To"] = receiver
    msg.set_content("\n".join(lines))
    msg.add_attachment(report_text.encode("utf-8"), maintype="application",
                       subtype="json", filename="test-report.json")
    return msg


def main():
    report_path = sys.argv[1] if len(sys.argv) > 1 else "test-report.json"
    server = os.environ.get("SMTP_SERVER") or "smtp.gmail.com"
    port = int(os.environ.get("SMTP_PORT") or 587)
    username = os.environ.get("SMTP_USERNAME", "")
    # Google shows app passwords as "abcd efgh ijkl mnop"; the spaces are not part of it.
    password = os.environ.get("SMTP_PASSWORD", "").replace(" ", "")
    receiver = os.environ.get("REPORT_EMAIL_TO", "")

    if not (username and password and receiver):
        print("Email not sent: SMTP_USERNAME, SMTP_PASSWORD or REPORT_EMAIL_TO is not set.")
        sys.exit(1)

    with open(report_path, encoding="utf-8") as f:
        report_text = f.read()
    report = json.loads(report_text)
    msg = build_email(report, report_text, username, receiver)

    with smtplib.SMTP(server, port, timeout=30) as smtp:
        smtp.starttls()
        smtp.login(username, password)
        smtp.send_message(msg)
    print(f"Email sent to {receiver}: {msg['Subject']}")


if __name__ == "__main__":
    main()
