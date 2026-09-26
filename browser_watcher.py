"""
Polls http://localhost:8000/api/health until it responds HTTP 200,
then opens the URL in the default browser. Runs as a separate process.
"""
import urllib.request
import subprocess
import time
import sys

URL    = "http://localhost:8000"
HEALTH = "http://localhost:8000/api/health"

deadline = time.time() + 90  # wait up to 90 seconds

while time.time() < deadline:
    try:
        r = urllib.request.urlopen(HEALTH, timeout=2)
        if r.status == 200:
            time.sleep(0.5)
            # Use explorer.exe — proven working on this machine
            subprocess.run(["explorer.exe", URL])
            sys.exit(0)
    except Exception:
        pass
    time.sleep(1.5)
