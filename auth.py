import os
from functools import wraps
from flask import request, jsonify, g
import jwt
from dotenv import load_dotenv
from database import banned_users_col

# Load environment variables
load_dotenv()

CLERK_JWKS_URL = os.getenv("CLERK_JWKS_URL")
ADMIN_EMAILS = [email.strip().lower() for email in os.getenv("ADMIN_EMAILS", "").split(",") if email.strip()]

# Lazy initialization of PyJWKClient to avoid crashing on import if URL is invalid/empty
jwks_client = None
if CLERK_JWKS_URL and CLERK_JWKS_URL.startswith("http"):
    try:
        jwks_client = jwt.PyJWKClient(CLERK_JWKS_URL)
    except Exception as e:
        print(f"Warning: Failed to initialize JWK client: {e}")

def get_token_from_header():
    """
    Extracts Bearer Token from Authorization Header.
    """
    auth_header = request.headers.get("Authorization", None)
    if not auth_header:
        return None
        
    parts = auth_header.split()
    if parts[0].lower() != "bearer":
        return None
    elif len(parts) == 1:
        return None
    elif len(parts) > 2:
        return None
        
    return parts[1]

def require_auth(f):
    """
    Decorator to protect routes and verify Clerk JWT.
    Supports local mockup headers for development testing.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        # Development override to test APIs without setting up Clerk
        mock_user = request.headers.get("X-Mock-User")
        if mock_user:
            g.user_id = mock_user
            g.user_email = request.headers.get("X-Mock-Email", "mock@college.edu")
            g.is_admin = g.user_email.lower() in ADMIN_EMAILS or mock_user == "user_admin"
            
            # Check if mock user is banned
            if banned_users_col.find_one({"userId": g.user_id}):
                return jsonify({"error": "Your account is banned due to code of conduct violation."}), 403
                
            return f(*args, **kwargs)

        if not CLERK_JWKS_URL or not jwks_client:
            return jsonify({"error": "Clerk authentication JWKS URL not configured in environment (CLERK_JWKS_URL)"}), 500

        token = get_token_from_header()
        if not token:
            return jsonify({"error": "Authentication token is missing"}), 401

        try:
            signing_key = jwks_client.get_signing_key_from_jwt(token)
            payload = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256"],
                options={"verify_aud": False}  # Clerk dynamic audience
            )
            
            # Populate globals
            g.user_id = payload.get("sub")
            
            # Clerk puts emails in payload under custom formats depending on standard claims
            # Generally, Clerk session JWTs have 'email' or 'email_address'
            g.user_email = (
                payload.get("email") or 
                payload.get("email_address") or 
                payload.get("primary_email_address") or 
                ""
            )
            
            # Check if administrator
            g.is_admin = g.user_email.lower() in ADMIN_EMAILS or g.user_id == "user_admin"

            # Check if user is banned in database
            if banned_users_col.find_one({"userId": g.user_id}):
                return jsonify({"error": "Your account is banned due to code of conduct violation."}), 403

        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Authentication token has expired"}), 401
        except jwt.InvalidTokenError as e:
            return jsonify({"error": f"Invalid authentication token: {str(e)}"}), 401
        except Exception as e:
            return jsonify({"error": f"Authentication validation failed: {str(e)}"}), 401

        return f(*args, **kwargs)
    return decorated

def admin_only(f):
    """
    Decorator to restrict route to administrators only.
    """
    @wraps(f)
    @require_auth
    def decorated(*args, **kwargs):
        if not getattr(g, "is_admin", False):
            return jsonify({"error": "Administrator privileges required"}), 403
        return f(*args, **kwargs)
    return decorated
