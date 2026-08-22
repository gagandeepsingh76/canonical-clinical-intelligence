"""
Manual integration test helper (disabled during automated pytest collection)
"""
if __name__ == "__main__":
    import requests
    resp = requests.post("http://127.0.0.1:8000/api/process")
    print("Status:", resp.status_code)
    print("Body:", resp.text[:1000])
