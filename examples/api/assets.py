# examples/api/assets.py

import os
import pprint
import requests
from dotenv import load_dotenv

load_dotenv()

BASE = os.getenv("PLANIT_BASE_URL", "http://127.0.0.1:8000")
USERNAME = os.getenv("PLANIT_USERNAME", "admin")
PASSWORD = os.getenv("PLANIT_PASSWORD", "password")

r = requests.get(
    f"{BASE}/api/assets/",
    auth=(USERNAME, PASSWORD),
    timeout=10,
)
print(r.status_code)
pprint.pp(r.json())
