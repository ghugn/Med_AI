import urllib.request
import json
import sys

case_id = "CASE_2F07B811"
url = f"http://127.0.0.1:8000/cases/{case_id}/extract"
print(f"Testing {url}")

req = urllib.request.Request(url, method="POST")
try:
    with urllib.request.urlopen(req) as response:
        data = response.read().decode('utf-8')
        parsed = json.loads(data)
        print(json.dumps(parsed, indent=2, ensure_ascii=False))
except Exception as e:
    print(f"HTTP Error: {e}")
