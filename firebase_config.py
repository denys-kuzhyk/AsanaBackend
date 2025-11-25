import firebase_admin
from firebase_admin import credentials, firestore

# Only initialize once
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase_key.json")
    firebase_admin.initialize_app(cred)


db = firestore.client()

# getting the email of a user with their ID
def get_user_email_with_id(id):
    email = db.collection("users").document(id).get().to_dict().get("email")

    return email

