import gspread
from gspread import Client
from src.core.config import settings

def get_gspread_client() -> Client:
    # Normalize the private key coming from environment/secrets.
    # GitHub Secrets or other stores sometimes save the PEM as a single-line
    # string with literal "\\n" sequences or with surrounding quotes. The
    # google auth loader expects real newlines in the PEM. Fix common cases here.
    raw_pk = settings.GOOGLE_PRIVATE_KEY or ""
    # Remove surrounding quotes if present
    if (raw_pk.startswith('"') and raw_pk.endswith('"')) or (
        raw_pk.startswith("'") and raw_pk.endswith("'")
    ):
        raw_pk = raw_pk[1:-1]

    # Replace literal \n sequences with real newlines
    private_key = raw_pk.replace("\\n", "\n")

    credentials = {
        "type": "service_account",
        "project_id": settings.GOOGLE_PROJECT_ID,
        "private_key_id": settings.GOOGLE_PRIVATE_KEY_ID,
        "private_key": private_key,
        "client_email": settings.GOOGLE_CLIENT_EMAIL,
        "client_id": "",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": settings.TOKEN_URI,
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": settings.GOOGLE_CLIENT_EMAIL,
    }

    return gspread.service_account_from_dict(credentials)

gspread_client = get_gspread_client()