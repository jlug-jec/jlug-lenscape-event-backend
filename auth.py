import os
from functools import wraps
from flask import request, jsonify, g
import jwt as pyjwt
from dotenv import load_dotenv
from database import banned_users_col, admins_col

load_dotenv()

USER_JWT_SECRET = os.getenv("USER_JWT_SECRET", "user-jwt-secret-change-me")
ADMIN_JWT_SECRET = os.getenv("ADMIN_JWT_SECRET", "change-me-in-production")


def _bearer_token():
    """Extract the Bearer token from the Authorization header."""
    auth_header = request.headers.get("Authorization", "")
    parts = auth_header.split()
    if len(parts) == 2 and parts[0].lower() == "bearer":
        return parts[1]
    return None


def require_auth(f):
    """
    Validate a Lenscape user session JWT (issued after Google / email-OTP auth).
    Supports X-Mock-User header for local development.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        # Dev override
        mock_user = request.headers.get("X-Mock-User")
        if mock_user:
            g.user_id = mock_user
            g.user_email = request.headers.get("X-Mock-Email", "mock@college.edu")
            g.is_admin = False
            if banned_users_col.find_one({"userId": g.user_id}):
                return jsonify({"error": "Your account is banned due to code of conduct violation."}), 403
            return f(*args, **kwargs)

        token = _bearer_token()
        if not token:
            return jsonify({"error": "Authentication token is missing"}), 401

        try:
            payload = pyjwt.decode(token, USER_JWT_SECRET, algorithms=["HS256"])
        except pyjwt.ExpiredSignatureError:
            return jsonify({"error": "Session has expired. Please sign in again."}), 401
        except pyjwt.InvalidTokenError:
            return jsonify({"error": "Invalid authentication token"}), 401

        g.user_id = payload.get("sub")
        g.user_email = payload.get("email", "")
        g.profile_complete = payload.get("profileComplete", False)
        g.is_admin = False

        if banned_users_col.find_one({"userId": g.user_id}):
            return jsonify({"error": "Your account is banned due to code of conduct violation."}), 403

        return f(*args, **kwargs)
    return decorated


def admin_only(f):
    """
    Restrict route to authenticated admins via the admin session JWT.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = _bearer_token()
        if not token:
            return jsonify({"error": "Administrator authentication required"}), 401

        try:
            payload = pyjwt.decode(token, ADMIN_JWT_SECRET, algorithms=["HS256"])
        except pyjwt.ExpiredSignatureError:
            return jsonify({"error": "Admin session expired"}), 401
        except pyjwt.InvalidTokenError:
            return jsonify({"error": "Invalid admin token"}), 401

        admin = admins_col.find_one({"email": payload.get("email")})
        if not admin:
            return jsonify({"error": "Administrator privileges required"}), 403

        g.user_id = payload.get("sub")
        g.user_email = payload.get("email")
        g.is_admin = True
        return f(*args, **kwargs)
    return decorated
