import hashlib
import datetime
from firebase_config import db
from flask_jwt_extended import create_access_token, create_refresh_token
from app import app

ACCESS_EXPIRE = datetime.timedelta(minutes=app.config["JWT_ACCESS_TOKEN_EXPIRES"])
REFRESH_EXPIRE = datetime.timedelta(minutes=app.config["JWT_REFRESH_TOKEN_EXPIRES"])

def create_session_and_tokens(user_id, session_id):

    # Set expiry durations
    access_expires = ACCESS_EXPIRE
    refresh_expires = REFRESH_EXPIRE

    # Generate tokens
    access_token = create_access_token(identity=user_id, expires_delta=access_expires, additional_claims={"session_id": session_id})
    refresh_token = create_refresh_token(identity=user_id, expires_delta=refresh_expires, additional_claims={"session_id": session_id})

    # Fingerprint the refresh token
    fingerprint = hashlib.sha256(refresh_token.encode()).hexdigest()

    # Timestamps
    now = datetime.datetime.now(datetime.timezone.utc)
    access_exp = now + access_expires
    refresh_exp = now + refresh_expires

    # Firestore session document
    session_data = {
        "session_id": session_id,
        "userId": user_id,
        "status": "active",
        "refreshFingerprint": fingerprint,
        "issuedAt": int(now.timestamp()),
        "lastRefreshAt": int(now.timestamp()),
        "refreshExp": int(refresh_exp.timestamp()),
        "accessExp": int(access_exp.timestamp()),
        "revoked": False
    }

    # Save session document
    db.collection("sessions").document(session_id).set(session_data)

    return {
        "access_token": access_token,
        "access_token_expires": int(access_exp.timestamp()),
        "refresh_token": refresh_token,
        "refresh_token_expires": int(refresh_exp.timestamp())
    }


def revoke_session(session_id):
    session_ref = db.collection("sessions").document(session_id)

    try:
        session_ref.update({"revoked": True})
        print(f"Session {session_id} successfully revoked.")

    except Exception as e:
        print(f"Failed to revoke session {session_id}: {e}")
