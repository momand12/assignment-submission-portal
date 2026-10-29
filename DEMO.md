# Demo: pass -> fail -> fix

This shows the whole workflow in three pushes:
(a) all tests pass, (b) a defect makes a test fail, (c) the fix makes everything pass again.
Each push shows the CI result, the automatically updated `test-report.json` on my laptop,
the email, and (on main) the GitHub Pages deploy.

Take the screenshots in the order of their numbers. They match the figure numbers in the report.

## Before you start

1. Double-click `start-receiver.bat`. The window says `Receiver listening on http://localhost:5050/report`.
2. Double-click `start-ngrok.bat`. The window says `Tunnel online: https://prelaunch-helpline-busybody.ngrok-free.dev`.
3. Keep both windows open until the end of the demo.
4. Open a terminal in the project folder and activate the virtual environment:
   ```
   cd Desktop\assignment-submission-portal
   .venv\Scripts\activate
   ```

**Setup screenshots**

| # | Screenshot |
|---|------------|
| 1 | GitHub: **Settings -> Secrets and variables -> Actions -> Secrets** tab, showing `REPORT_URL`, `REPORT_TOKEN`, `SMTP_USERNAME`, `SMTP_PASSWORD` (only names are shown, never values). |
| 2 | Same page, **Variables** tab, showing `REPORT_EMAIL_TO`. |
| 3 | GitHub: **Settings -> Pages**, showing Source = **GitHub Actions** and the site URL. |
| 4 | Both black windows (receiver and ngrok) side by side, running. |
| 5 | The portal running locally: `python app.py`, open http://localhost:5000, submit one valid entry and try one with an empty registration number, so the red message is visible. |

## (a) Push: all tests pass

1. Run the tests locally: `pytest -v` -> **8 passed**.
2. Make any small change (for example add a line to README), then:
   ```
   git add README.md
   git commit -m "Demo (a): small README update"
   git push
   ```
3. Open https://github.com/momand12/assignment-submission-portal/actions and wait about 30 seconds.

| # | Screenshot |
|---|------------|
| 6 | Actions list: the new run with a **green tick**. |
| 7 | The run page: job graph with **test ✓** and **deploy ✓**. |
| 8 | test job -> **Run tests** step opened: 8 tests `PASSED`. |
| 9 | test job -> **Send report to local receiver** step: `Report saved.` |
| 10 | The receiver window: new log line `status=PASSED passed=8/8`. |
| 11 | `test-report.json` opened (Notepad or VS Code): run_number, commit_sha, `"overall_status": "passed"`. |
| 12 | Gmail inbox: email **[PASSED] CI report - <short SHA>**. |
| 13 | The email opened: commit SHA, result, counts, each test, and the `test-report.json` attachment. |
| 14 | Pages site https://momand12.github.io/assignment-submission-portal/ with one submission saved, and the red message for an invalid URL. |
| 15 | GitHub: repo home page -> **Deployments** (right side) -> `github-pages`: the latest deployment comes from this commit. |

## (b) Introduce a defect: a test fails

1. Open `app.py`, find this line in `validate()`:
   ```python
       if not is_valid_url(form["submission_url"].strip()):
   ```
   and replace it with this one line (the URL check now accepts everything):
   ```python
       if False:  # DEFECT: URL check turned off
   ```
2. Run the tests locally: `pytest -v` -> **5 failed, 3 passed**, including
   `test_invalid_url_is_rejected_and_not_saved`.
3. Push it anyway (this is the demo of a broken change):
   ```
   git add app.py
   git commit -m "Demo (b): introduce defect - URL check turned off"
   git push
   ```

| # | Screenshot |
|---|------------|
| 16 | Terminal: local `pytest -v` showing the failed tests. |
| 17 | Actions list: the new run with a **red cross**. |
| 18 | The run page: **test ✗** and **deploy skipped** (grey). The deploy job did not run because of `needs: test`. |
| 19 | test job -> **Run tests** step: `FAILED tests/test_app.py::test_invalid_url_is_rejected_and_not_saved` with `AssertionError: an invalid URL should be rejected`. |
| 20 | test job: **Make JSON test report** and **Send report to local receiver** still ran (green) after the failed step, because of `if: always()`. |
| 21 | The receiver window: new log line `status=FAILED passed=3/8`. |
| 22 | `test-report.json`: `"overall_status": "failed"`, `"failed": 5`, and the `failure_message` of the failed tests. |
| 23 | Gmail: email **[FAILED] CI report - <short SHA>**, opened, showing the failed tests. |
| 24 | **Deployments -> github-pages**: still the deployment from step (a). The old site was left unchanged. |

## (c) Fix the defect: all pass again

1. In `app.py`, put the original line back:
   ```python
       if not is_valid_url(form["submission_url"].strip()):
   ```
2. Run the tests locally: `pytest -v` -> **8 passed**.
3. Push the fix:
   ```
   git add app.py
   git commit -m "Demo (c): fix defect - restore URL check"
   git push
   ```

| # | Screenshot |
|---|------------|
| 25 | Actions list: three demo runs, **green, red, green**. |
| 26 | The run page: **test ✓** and **deploy ✓**. |
| 27 | The receiver window: all three log lines (PASSED, FAILED, PASSED). |
| 28 | `test-report.json`: the new commit_sha and `"overall_status": "passed"`. |
| 29 | The `reports/` folder in File Explorer: one `report-<run_id>.json` per run. |
| 30 | Gmail inbox: the three emails, **[PASSED]**, **[FAILED]**, **[PASSED]**. |
| 31 | **Deployments -> github-pages**: a new deployment from the fix commit. |
