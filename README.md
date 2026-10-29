# Assignment Submission Portal

**Name:** Hamad Khan Momand
**Registration number:** FA23-BSE-060
**Course:** CSC418 DevOps, Lab Midterm (COMSATS University Islamabad, Attock Campus)

**Live demo (GitHub Pages):** https://momand12.github.io/assignment-submission-portal/

## What this project does

- A small **Flask web portal** where a student enters their name, registration number,
  assignment title and submission URL. All four fields are required, and the URL must be a
  valid `http`/`https` URL with a proper domain. Valid submissions are saved in
  `submissions.json` and listed in a "Saved Submissions" table. Invalid ones are rejected
  with a red validation message and are not saved.
- **Automated tests** (pytest) that run on **every push** with GitHub Actions.
- After every run (pass or fail), CI turns the test results into a **JSON report** and sends it
  through an **ngrok tunnel** to a small **receiver on my laptop**, which saves it as
  `test-report.json`.
- **Bonus 1:** if all tests pass on `main`, a static demo (in `site/`) is published to GitHub Pages.
- **Bonus 2:** the report is also **emailed** after every run.

## Project structure

```
app.py                     Flask portal (port 5000)
templates/index.html       Portal page
tests/test_app.py          pytest tests (use a temporary data file)
ci/make_report.py          JUnit XML -> test-report.json
ci/send_email.py           Emails the report (smtplib)
receiver/receiver.py       Local report receiver (port 5050, POST /report)
receiver/tunnel.py         ngrok tunnel (static domain -> localhost:5050)
start-receiver.bat         Double-click to start the receiver
start-ngrok.bat            Double-click to start the ngrok tunnel
setup-ngrok-token.bat      One-time: save the ngrok authtoken
site/                      Static demo for GitHub Pages (localStorage)
.github/workflows/ci.yml   CI pipeline
DEMO.md                    Demo steps and screenshot list
PROBLEMS.md                Problems faced and fixes
```

## Run the app

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows (Linux/Mac: source .venv/bin/activate)
pip install -r requirements.txt
python app.py
```

Then open http://localhost:5000

## Run the tests

```bash
pytest -v
```

The tests use pytest's `tmp_path`, so they never touch the real `submissions.json`.

## Start the receiver and the ngrok tunnel

Both must stay open while you push and during the demo.

1. **Receiver:** double-click `start-receiver.bat` (or run `python receiver/receiver.py`).
   It listens on `http://localhost:5050/report`. Port 5050 is used so it does not clash
   with the Flask app on port 5000. The secret token is read from `receiver/token.txt`
   (not in git) or the `REPORT_TOKEN` environment variable.
2. **ngrok tunnel:** double-click `start-ngrok.bat` (or run `python receiver/tunnel.py`).
   It forwards `https://prelaunch-helpline-busybody.ngrok-free.dev` (my free static
   domain) to `localhost:5050`.
   - It uses ngrok's official Python package (`pip install -r receiver/requirements.txt`)
     instead of `ngrok.exe`, because Windows Defender blocks `ngrok.exe` on my laptop
     (see `PROBLEMS.md`).
   - One-time setup: double-click `setup-ngrok-token.bat` and paste the authtoken from the
     ngrok dashboard. It is saved in ngrok's own config file, not in this repo.

When a report arrives, the receiver prints a log line and saves:
- `test-report.json` (latest report, in the project folder)
- `reports/report-<run_id>.json` (a copy of every run)

## GitHub secrets and variables

Set in **Settings -> Secrets and variables -> Actions**.

| Name | Type | Value |
|------|------|-------|
| `REPORT_URL` | Secret | `https://prelaunch-helpline-busybody.ngrok-free.dev/report` |
| `REPORT_TOKEN` | Secret | same value as `receiver/token.txt` |
| `SMTP_USERNAME` | Secret | sender Gmail address |
| `SMTP_PASSWORD` | Secret | Gmail **app password** (16 characters) |
| `REPORT_EMAIL_TO` | Variable | address that receives the report emails |

The SMTP server and port default to `smtp.gmail.com` and `587`.

## CI pipeline (`.github/workflows/ci.yml`)

**Job `test`** (every push, every branch):
1. Check out the pushed commit, set up Python, install requirements.
2. `pytest -v --junitxml=results.xml`. A failing test fails this step and the job.
3. `if: always()` steps: make `test-report.json`, upload it as an artifact,
   send it to the receiver with curl (`continue-on-error: true`), and email it
   (`continue-on-error: true`).

**Job `deploy`** (`needs: test`, only on `main`): publishes `site/` to GitHub Pages with the
official Pages actions. If any test fails, this job is skipped and the old site stays live.
Pages source must be set to **GitHub Actions** (Settings -> Pages -> Source).
