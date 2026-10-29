"""Automated tests for the Assignment Submission Portal.

Every test uses its own temporary submissions file (pytest's tmp_path),
so the real submissions.json is never touched.
"""
import json

import pytest

from app import app

VALID = {
    "name": "Hamad Khan Momand",
    "registration_number": "FA23-BSE-060",
    "assignment_title": "Lab Midterm",
    "submission_url": "https://github.com/momand12/assignment-submission-portal",
}


@pytest.fixture
def data_file(tmp_path):
    return tmp_path / "submissions.json"


@pytest.fixture
def client(data_file):
    app.config["TESTING"] = True
    app.config["DATA_FILE"] = str(data_file)
    return app.test_client()


def saved_submissions(data_file):
    if not data_file.exists():
        return []
    return json.loads(data_file.read_text(encoding="utf-8"))


def test_valid_submission_is_saved_and_listed(client, data_file):
    response = client.post("/", data=VALID, follow_redirects=True)
    page = response.get_data(as_text=True)

    assert response.status_code == 200, "a valid submission should be accepted"
    assert "Submission saved." in page
    # Listed on the page
    assert "Saved Submissions" in page
    assert "FA23-BSE-060" in page
    assert VALID["submission_url"] in page
    # Saved in the data file
    saved = saved_submissions(data_file)
    assert len(saved) == 1
    assert saved[0]["registration_number"] == "FA23-BSE-060"


def test_missing_registration_number_is_rejected(client, data_file):
    data = dict(VALID, registration_number="")
    response = client.post("/", data=data)
    page = response.get_data(as_text=True)

    assert response.status_code == 400, "a submission without registration number should be rejected"
    assert "Registration number is required." in page, "the validation message should be shown"
    assert saved_submissions(data_file) == [], "a rejected submission must not be saved"


def test_invalid_url_is_rejected_and_not_saved(client, data_file):
    data = dict(VALID, submission_url="not-a-valid-url")
    response = client.post("/", data=data)
    page = response.get_data(as_text=True)

    assert response.status_code == 400, "an invalid URL should be rejected"
    assert "Submission URL must be a valid http or https URL" in page, "the validation message should be shown"
    assert saved_submissions(data_file) == [], "a rejected submission must not be saved"


@pytest.mark.parametrize("bad_url", ["ftp://github.com/file", "https://localhost", "http://", "https://exa mple.com"])
def test_url_without_http_or_proper_domain_is_rejected(client, data_file, bad_url):
    response = client.post("/", data=dict(VALID, submission_url=bad_url))

    assert response.status_code == 400, f"{bad_url!r} should be rejected"
    assert saved_submissions(data_file) == [], "a rejected submission must not be saved"


def test_home_page_shows_form_and_empty_list(client):
    response = client.get("/")
    page = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Assignment Submission Portal" in page
    assert "No submissions yet." in page
