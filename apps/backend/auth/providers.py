import firebase_admin
from firebase_admin import credentials, auth
from google.oauth2 import id_token
from google.auth.transport import requests
from core.config import settings
from loguru import logger

# Initialize Firebase Admin SDK
try:
    if not firebase_admin._apps:
        # Check if we have minimum required keys to init (even dummy ones for dev)
        if settings.FIREBASE_PROJECT_ID and settings.FIREBASE_CLIENT_EMAIL:
            # We reconstruct the private key string in case it has escaped newlines
            private_key = settings.FIREBASE_PRIVATE_KEY.replace('\\n', '\n') if settings.FIREBASE_PRIVATE_KEY else ""
            
            cred = credentials.Certificate({
                "type": "service_account",
                "project_id": settings.FIREBASE_PROJECT_ID,
                "private_key_id": settings.FIREBASE_PRIVATE_KEY_ID,
                "private_key": private_key,
                "client_email": settings.FIREBASE_CLIENT_EMAIL,
                "client_id": settings.FIREBASE_CLIENT_ID,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_x509_cert_url": settings.FIREBASE_CLIENT_X509_CERT_URL
            })
            firebase_admin.initialize_app(cred)
            logger.info("Firebase Admin initialized successfully.")
        else:
            logger.warning("Firebase Admin skipped: missing configuration.")
except Exception as e:
    logger.warning(f"Firebase Admin skipped (invalid or missing keys): {e}")

def verify_firebase_token(token: str) -> dict:
    """
    Verify Firebase ID token (used for Phone OTP).
    Returns a dict with user info if successful, raises exception if invalid.
    """
    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except Exception as e:
        logger.error(f"Firebase token verification failed: {e}")
        raise ValueError("Invalid Firebase ID token")

def verify_google_token(token: str) -> dict:
    """
    Verify Google OAuth ID token.
    Returns a dict with user info if successful, raises exception if invalid.
    """
    try:
        # Specify the CLIENT_ID of the app that accesses the backend
        idinfo = id_token.verify_oauth2_token(
            token, 
            requests.Request(), 
            settings.GOOGLE_CLIENT_ID
        )
        return idinfo
    except Exception as e:
        logger.error(f"Google token verification failed: {e}")
        raise ValueError("Invalid Google OAuth ID token")
