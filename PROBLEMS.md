# Problems Faced

Every problem we hit while building the project, what caused it, and how we fixed it.

| # | Problem | Cause | Fix |
|---|---------|-------|-----|
| 1 | GitHub CLI was logged in as another student's account (`iabdullahjan`). | The laptop is shared, and gh had two accounts with the other one active. | Ran `gh auth switch -u momand12` and checked with `gh api user`. |
| 2 | `winget install ngrok.ngrok` said "No package found". | The winget package ID is `Ngrok.Ngrok`, not `ngrok.ngrok`. | Ran `winget search ngrok` to find the right ID, then `winget install Ngrok.Ngrok`. |
| 3 | After `ngrok update`, Windows Defender blocked the new ngrok version (3.39.13) as `Trojan:Win32/Kepavll!rfn`. | Antivirus programs often flag tunnel tools like ngrok, because attackers also use them. | We did not turn off or bypass the antivirus. The old version (3.3.1) installed by winget was still there and working. |
| 4 | My first "defect" for the demo (making the last line of `is_valid_url` return True) did not fail the required `test_invalid_url_is_rejected_and_not_saved` test. | The scheme check (`http`/`https`) ran before that line, so `not-a-valid-url` was still rejected. | Moved the demo defect into `validate()` (`if False:` instead of the URL check), which really accepts every URL. Tested it locally: the required test fails. |
| 5 | Could not check the JavaScript validation from the command line. | Node.js is not installed on this laptop. | Served `site/` with `python -m http.server` and tested `isValidUrl()` and the form in a browser. Results matched the Python version exactly. |
