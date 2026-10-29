"""Start the ngrok tunnel: https://<my static domain>  ->  http://localhost:5050

Uses ngrok's official Python package (pip install ngrok) instead of ngrok.exe,
because Windows Defender blocks ngrok.exe on this laptop and the old version
that is not blocked is rejected by ngrok as too old.

The authtoken is read from the NGROK_AUTHTOKEN environment variable, or from
the ngrok config file that "ngrok config add-authtoken" created
(setup-ngrok-token.bat). It is never written in this code.

Run it with:  python receiver/tunnel.py   (or double-click start-ngrok.bat)
"""
import os
import time
from datetime import datetime

import ngrok

DOMAIN = "prelaunch-helpline-busybody.ngrok-free.dev"
LOCAL_PORT = 5050
CONFIG_FILE = os.path.join(os.environ.get("LOCALAPPDATA", ""), "ngrok", "ngrok.yml")


def load_authtoken():
    token = os.environ.get("NGROK_AUTHTOKEN", "").strip()
    if token:
        return token
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, encoding="utf-8") as f:
            for line in f:
                if line.strip().startswith("authtoken:"):
                    return line.split(":", 1)[1].strip().strip('"')
    return ""


def log(message):
    print(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] {message}", flush=True)


if __name__ == "__main__":
    token = load_authtoken()
    if not token:
        print("ERROR: no ngrok authtoken. Double-click setup-ngrok-token.bat first.")
        raise SystemExit(1)

    listener = ngrok.forward(f"localhost:{LOCAL_PORT}", authtoken=token, domain=DOMAIN)
    log(f"Tunnel online: {listener.url()}  ->  http://localhost:{LOCAL_PORT}")
    log(f"GitHub secret REPORT_URL should be: {listener.url()}/report")
    log("Keep this window open while you push and during the demo. Ctrl+C to stop.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        log("Tunnel stopped.")
