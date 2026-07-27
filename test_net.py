import requests

try:
    r = requests.get("https://api.groq.com")
    print("STATUS:", r.status_code)
    print("TEXT:", r.text[:100])
except Exception as e:
    print("ERROR:", repr(e))