import os

# Google Cloud & Gemini Configuration
_raw_proj = os.getenv("GOOGLE_CLOUD_PROJECT", "stable-century-479407-m7")
PROJECT_ID = _raw_proj.split()[0].split(",")[0].strip()
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1").strip()
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash").split()[0].strip()

# Stanford AI4PB Lab Metadata
LAB_NAME = "Stanford AI for Public Benefit Lab (AI4PB)"
LAB_URL = "https://ai4pb.stanford.edu/"
LAB_DIRECTOR = "Professor Robb Willer"
