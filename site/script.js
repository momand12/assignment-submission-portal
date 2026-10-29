// Static demo of the portal. Same validation as app.py,
// but submissions are saved in the browser's localStorage.

const STORAGE_KEY = "submissions";

const FIELDS = {
  name: "Name",
  registration_number: "Registration number",
  assignment_title: "Assignment title",
  submission_url: "Submission URL",
};

// Same rule as DOMAIN_PATTERN in app.py, e.g. "github.com"
const DOMAIN_PATTERN = /^[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)+$/;

function isValidUrl(text) {
  // A space anywhere means it is not a proper URL (same as the Flask app).
  if (/\s/.test(text)) return false;
  let url;
  try {
    url = new URL(text);
  } catch {
    return false;
  }
  if (url.protocol !== "http:" && url.protocol !== "https:") return false;
  return DOMAIN_PATTERN.test(url.hostname);
}

function validate(data) {
  for (const [field, label] of Object.entries(FIELDS)) {
    if (!data[field]) return `${label} is required.`;
  }
  if (!isValidUrl(data.submission_url)) {
    return "Submission URL must be a valid http or https URL (for example https://github.com/user/repo).";
  }
  return null;
}

function loadSubmissions() {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY)) || [];
  } catch {
    return [];
  }
}

function saveSubmissions(list) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(list));
}

function showList() {
  const list = loadSubmissions();
  const rows = document.getElementById("rows");
  rows.innerHTML = "";
  list.forEach((s, i) => {
    const tr = document.createElement("tr");
    // textContent (not innerHTML) so typed text can never run as code
    [i + 1, s.name, s.registration_number, s.assignment_title].forEach((value) => {
      const td = document.createElement("td");
      td.textContent = value;
      tr.appendChild(td);
    });
    const urlCell = document.createElement("td");
    const link = document.createElement("a");
    link.href = s.submission_url;
    link.textContent = s.submission_url;
    link.target = "_blank";
    link.rel = "noopener";
    urlCell.appendChild(link);
    tr.appendChild(urlCell);
    const timeCell = document.createElement("td");
    timeCell.textContent = s.submitted_at;
    tr.appendChild(timeCell);
    rows.appendChild(tr);
  });
  document.getElementById("table").hidden = list.length === 0;
  document.getElementById("empty").hidden = list.length > 0;
}

document.getElementById("form").addEventListener("submit", (event) => {
  event.preventDefault();
  const errorBox = document.getElementById("error");
  const successBox = document.getElementById("success");

  const data = {};
  for (const field of Object.keys(FIELDS)) {
    data[field] = document.getElementById(field).value.trim();
  }

  const error = validate(data);
  if (error) {
    errorBox.textContent = error;
    errorBox.hidden = false;
    successBox.hidden = true;
    return; // rejected: nothing is saved
  }

  data.submitted_at = new Date().toISOString().slice(0, 16).replace("T", " ") + " UTC";
  const list = loadSubmissions();
  list.push(data);
  saveSubmissions(list);

  errorBox.hidden = true;
  successBox.hidden = false;
  event.target.reset();
  showList();
});

document.getElementById("clear").addEventListener("click", () => {
  localStorage.removeItem(STORAGE_KEY);
  showList();
});

showList();
