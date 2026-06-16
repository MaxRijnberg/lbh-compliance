from lbh_compliance.config.secrets import secrets

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[3]

# API General
API_TIMEOUT = 30

# PortAble settings
PORTABLE_BASE_URL = "https://backend.lbh-portableagent.com/core/api/v1/"
PORTABLE_EMAIL = secrets["portable_credentials"]["email"]
PORTABLE_PASSWORD = secrets["portable_credentials"]["password"]

# Pascal settings
PASCAL_BASE_URL = "https://app.pascal.vartion.com"
PASCAL_AUTH_TOKEN = secrets["pascal_credentials"]["auth_token"]
PASCAL_ORG_ID = secrets["pascal_credentials"]["organisation_id"]
PASCAL_HEADERS = {
    "Authorization": f"Bearer {PASCAL_AUTH_TOKEN}",
    "OrganizationId": PASCAL_ORG_ID,
    "Content-Type": "application/json",
    "Accept": "application/json",
}

LOG_DIR = BASE_DIR / "logs"

# Front end colours
SCREENING_COLOURS = {0: "#27F549", 1: "#F5B027", 2: "#9C2007"}
