import gspread
from gspread import Client
from src.core.config import settings

def get_gspread_client() -> Client:
    credentials = {
        "type": "service_account",
        "project_id": settings.GOOGLE_PROJECT_ID,
        "private_key_id": settings.GOOGLE_PRIVATE_KEY_ID,
        "private_key": settings.GOOGLE_PRIVATE_KEY,
        "client_email": settings.GOOGLE_CLIENT_EMAIL,
        "client_id": "",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": settings.TOKEN_URI,
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": settings.GOOGLE_CLIENT_EMAIL
    }
    return gspread.service_account_from_dict(credentials)

gspread_client = get_gspread_client()