import sys

import requests

filename = sys.argv[1]

if filename == "gitleaks.json":
    scan_type = "Gitleaks Scan"
elif filename == "semgrep.json":
    scan_type = "Semgrep JSON Report"

headers = {"Authorization": "Token a067833d35bfa45fe1011dec721b404efd7e1618"}

url = "https://demo.defectdojo.org/api/v2/import-scan/"

data = {"active": True, "verified": True, "scan_type": scan_type, "minimum_severity": "Low", "engagement": 22}

files = {"file": open(filename, "rb")}

r = requests.post(url, headers=headers, data=data, files=files)

if r.status_code == 201:
    print(f"Scan {filename} results imported successfully!")
else:
    print(f"Failed to import scan {filename} results: {r.content}")
