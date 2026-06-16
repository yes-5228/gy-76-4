import os


DATA_FILE = os.getenv("DATA_FILE", os.path.join(os.path.dirname(__file__), "..", "data", "attendance-system.json"))
RENEWAL_THRESHOLD = int(os.getenv("RENEWAL_THRESHOLD", "4"))
