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

# SeaSearcher settings
SEASEARCHER_BASE_URL = "https://api.lloydslistintelligence.com/v1"
SEASEARCHER_USERNAME = secrets["seasearcher_credentials"]["username"]
SEASEARCHER_PASSWORD = secrets["seasearcher_credentials"]["password"]

LOG_DIR = BASE_DIR / "logs"

# Front end mapping
SCREENING_STATUSES = {0: "", 1: "- Unresolved sanction hits", 2: "- SANCTIONED ENTITY"}

# Front end colours
SCREENING_COLOURS = {0: "#09741B", 1: "#C08000", 2: "#9C2007"}
