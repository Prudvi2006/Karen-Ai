import requests
import os

def download_file(url, filename):
    os.makedirs("temp", exist_ok=True)
    path = os.path.join("temp", filename)

    r = requests.get(url)
    with open(path, "wb") as f:
        f.write(r.content)

    return path