"""Local report receiver.

A tiny HTTP server that runs on my laptop (port 5050). GitHub Actions sends
the JSON test report to POST /report through the ngrok tunnel. The receiver:
  1. checks the secret token in the X-Report-Token header,
  2. saves the report as test-report.json in the project folder,
  3. keeps a copy of every run as reports/report-<run_id>.json,
  4. prints a log line.

Run it with:  python receiver/receiver.py   (or double-click start-receiver.bat)
"""
import hmac
import json
import os
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = 5050
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORT_FILE = os.path.join(PROJECT_DIR, "test-report.json")
REPORTS_DIR = os.path.join(PROJECT_DIR, "reports")
TOKEN_FILE = os.path.join(PROJECT_DIR, "receiver", "token.txt")


def load_token():
    """The token comes from the REPORT_TOKEN env variable or receiver/token.txt."""
    token = os.environ.get("REPORT_TOKEN", "").strip()
    if not token and os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, encoding="utf-8") as f:
            token = f.read().strip()
    return token


TOKEN = load_token()


def log(message):
    print(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] {message}", flush=True)


class ReportHandler(BaseHTTPRequestHandler):
    def reply(self, status, text):
        body = (text + "\n").encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        # Handy check that the tunnel works: open the ngrok URL in a browser.
        self.reply(200, "Report receiver is running. Send reports with POST /report.")

    def do_POST(self):
        if self.path != "/report":
            self.reply(404, "Not found. Use POST /report.")
            return

        # 1. Check the secret token
        sent_token = self.headers.get("X-Report-Token", "")
        if not hmac.compare_digest(sent_token, TOKEN):
            log(f"REJECTED report from {self.client_address[0]}: wrong or missing token")
            self.reply(401, "Unauthorized: wrong or missing X-Report-Token header.")
            return

        # 2. Read the body and make sure it is JSON
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        try:
            report = json.loads(body)
        except ValueError:
            log("REJECTED report: body is not valid JSON")
            self.reply(400, "Bad request: body must be JSON.")
            return

        # 3. Save as test-report.json and keep a copy per run
        text = json.dumps(report, indent=2)
        with open(REPORT_FILE, "w", encoding="utf-8") as f:
            f.write(text)
        os.makedirs(REPORTS_DIR, exist_ok=True)
        copy_path = os.path.join(REPORTS_DIR, f"report-{report.get('run_id', 'unknown')}.json")
        with open(copy_path, "w", encoding="utf-8") as f:
            f.write(text)

        # 4. Log line
        log(
            f"Report received: run #{report.get('run_number')} "
            f"branch={report.get('branch')} commit={str(report.get('commit_sha'))[:7]} "
            f"status={str(report.get('overall_status')).upper()} "
            f"passed={report.get('passed')}/{report.get('total')} "
            f"-> saved test-report.json and reports/{os.path.basename(copy_path)}"
        )
        self.reply(200, "Report saved.")

    def log_message(self, format, *args):
        # Hide the default noisy request log; we print our own lines.
        pass


if __name__ == "__main__":
    if not TOKEN:
        print("ERROR: no token. Put it in receiver/token.txt or set REPORT_TOKEN.")
        raise SystemExit(1)
    server = HTTPServer(("127.0.0.1", PORT), ReportHandler)
    log(f"Receiver listening on http://localhost:{PORT}/report  (Ctrl+C to stop)")
    log(f"Reports will be saved to {REPORT_FILE}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        log("Receiver stopped.")
