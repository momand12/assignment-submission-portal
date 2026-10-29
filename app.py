"""Assignment Submission Portal - a small Flask app.

Students enter their name, registration number, assignment title and
submission URL. Valid submissions are saved in a JSON file and listed on
the page. Invalid ones are rejected with a validation message.
"""
import json
import os
import re
from datetime import datetime, timezone
from urllib.parse import urlparse

from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)

# Where submissions are saved. Tests change this to a temporary file.
app.config["DATA_FILE"] = os.path.join(os.path.dirname(__file__), "submissions.json")

# The four form fields and their labels (used in validation messages).
FIELDS = {
    "name": "Name",
    "registration_number": "Registration number",
    "assignment_title": "Assignment title",
    "submission_url": "Submission URL",
}

# A domain like "github.com" or "drive.google.com": letters/digits/hyphens
# separated by dots, at least one dot.
DOMAIN_PATTERN = re.compile(r"^[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)+$")


def is_valid_url(url):
    """Return True only for http/https URLs that have a proper domain."""
    parts = urlparse(url)
    if parts.scheme not in ("http", "https"):
        return False
    host = parts.hostname or ""
    return bool(DOMAIN_PATTERN.match(host))


def validate(form):
    """Return an error message for the first problem found, or None if OK."""
    for field, label in FIELDS.items():
        if not form.get(field, "").strip():
            return f"{label} is required."
    if not is_valid_url(form["submission_url"].strip()):
        return "Submission URL must be a valid http or https URL (for example https://github.com/user/repo)."
    return None


def load_submissions():
    path = app.config["DATA_FILE"]
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_submission(submission):
    submissions = load_submissions()
    submissions.append(submission)
    with open(app.config["DATA_FILE"], "w", encoding="utf-8") as f:
        json.dump(submissions, f, indent=2)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        error = validate(request.form)
        if error:
            # Rejected: show the message, keep what the student typed, save nothing.
            return render_template(
                "index.html",
                error=error,
                form=request.form,
                submissions=load_submissions(),
            ), 400

        submission = {field: request.form[field].strip() for field in FIELDS}
        submission["submitted_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        save_submission(submission)
        # Redirect after saving so refreshing the page does not submit twice.
        return redirect(url_for("index", saved=1))

    return render_template(
        "index.html",
        error=None,
        form={},
        saved=request.args.get("saved") == "1",
        submissions=load_submissions(),
    )


if __name__ == "__main__":
    app.run(port=5000, debug=True)
