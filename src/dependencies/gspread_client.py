import json
import os
import gspread
from gspread import Client
from src.core.config import settings


def get_gspread_client() -> Client:
    """Create a gspread client from several possible credential sources.

    The function supports:
    - Loading a JSON credentials file pointed by GOOGLE_APPLICATION_CREDENTIALS.
    - Parsing the full service account JSON stored in an env var.
    - Using a PEM private key stored (possibly escaped) in GOOGLE_PRIVATE_KEY.
    """
    # 1) If GOOGLE_APPLICATION_CREDENTIALS is a path to a JSON file, load it.
    creds_path = getattr(settings, "GOOGLE_APPLICATION_CREDENTIALS", None)
    if creds_path:
        try:
            if os.path.exists(creds_path):
                with open(creds_path, "r", encoding="utf-8") as fh:
                    data = json.load(fh)
                    return gspread.service_account_from_dict(data)
        except Exception:
            # Fall through to other resolution strategies
            pass

    # 2) Try to handle the case where the full service-account JSON was stored
    # directly in an env var (some CI setups do this).
    raw = getattr(settings, "GOOGLE_PRIVATE_KEY", None) or ""
    if raw.strip().startswith("{"):
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, dict) and parsed.get("private_key"):
                return gspread.service_account_from_dict(parsed)
        except Exception:
            pass

    # 3) Normalize PEM-like private key strings. Handle common escaping and quoting.
    pk = raw
    if (pk.startswith('"') and pk.endswith('"')) or (pk.startswith("'") and pk.endswith("'")):
        pk = pk[1:-1]
    pk = pk.replace("\\\\n", "\\n")
    pk = pk.replace("\\n", "\n")
    pk = pk.replace("\r", "")

    # As a last resort, maybe the whole JSON was put in GOOGLE_APPLICATION_CREDENTIALS
    alt = getattr(settings, "GOOGLE_APPLICATION_CREDENTIALS", None)
    if alt and alt.strip().startswith("{"):
        try:
            parsed = json.loads(alt)
            if isinstance(parsed, dict) and parsed.get("private_key"):
                return gspread.service_account_from_dict(parsed)
        except Exception:
            pass

    credentials = {
        "type": "service_account",
        "project_id": settings.GOOGLE_PROJECT_ID,
        "private_key_id": settings.GOOGLE_PRIVATE_KEY_ID,
        "private_key": pk,
        "client_email": settings.GOOGLE_CLIENT_EMAIL,
        "client_id": "",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": settings.TOKEN_URI,
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": settings.GOOGLE_CLIENT_EMAIL,
    }

    try:
        return gspread.service_account_from_dict(credentials)
    except Exception as exc:
        msg = (
            "Failed to create gspread client from provided credentials. "
            f"private_key length={len(pk) if pk else 0}, "
            f"project_id set={bool(settings.GOOGLE_PROJECT_ID)}"
        )
        raise RuntimeError(msg) from exc


# Do not create a global client at import time; callers should call
# `get_gspread_client()` when they need a client. This avoids import-time
# failures in CI when credentials aren't available.