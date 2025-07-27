import requests

API_BASE = "http://backend:8000"

def analyze_media(file):
    files = {"file": (file.name, file, file.type)}
    response = requests.post(f"{API_BASE}/upload/media", files=files, params={"overwrite": "true"})

    print("📡 Status Code:", response.status_code)
    print("📡 Response Text:", response.text[:500])

    response.raise_for_status()
    return response.json()

def rag_search_query(payload):
    response = requests.post(f"{API_BASE}/rag/custom", json=payload)
    return response.json()


def keyword_search(payload):
    response = requests.get(f"{API_BASE}/search/media", params=payload)
    return response.json()

