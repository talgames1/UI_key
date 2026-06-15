import os
import json
import sys

try:
    import firebase_admin
    from firebase_admin import credentials, firestore
except ImportError:
    print("ERROR: firebase-admin is not installed. Run 'pip install firebase-admin' first.")
    sys.exit(1)

SERVICE_ACCOUNT_FILE = os.path.join(os.path.dirname(__file__), "hash-code-ai-reg-firebase-adminsdk-fbsvc-ce391a6d18.json")
SERVICE_ACCOUNT_ENV = "FIREBASE_SERVICE_ACCOUNT_PATH"
DOCUMENT_PATH = ("access_control", "app_hash")


def load_credentials_path():
    env_path = os.getenv(SERVICE_ACCOUNT_ENV)
    if env_path:
        return env_path
    return SERVICE_ACCOUNT_FILE


def init_firestore():
    path = load_credentials_path()
    if not os.path.exists(path):
        print(f"❌ERROR: Service account file not found: {path}")
        return None

    try:
        cred = credentials.Certificate(path)
        app = firebase_admin.initialize_app(cred)
        db = firestore.client()
        return db
    except Exception as exc:
        print(f"❌ERROR: Firebase initialization failed: {exc}")
        return None


def check_hash_document(db):
    collection, document = DOCUMENT_PATH
    try:
        doc_ref = db.collection(collection).document(document)
        doc = doc_ref.get()
        if not doc.exists:
            print(f"⚠️WARNING: Firestore document not found: {collection}/{document}")
            return False
        data = doc.to_dict()
        if not data or "hash" not in data:
            print(f"⚠️WARNING: Document exists but missing 'hash' field: {collection}/{document}")
            return False
        print(f"✅SUCCESS: Firestore document found and hash field is present.")
        print(f"Document path: {collection}/{document}")
        return True
    except Exception as exc:
        print(f"❌ERROR: Failed to read Firestore document: {exc}")
        return False


def main():
    print("Firebase Firestore health check")
    print("--------------------------------")
    db = init_firestore()
    if not db:
        sys.exit(1)

    print("Firebase initialization succeeded.")
    if not check_hash_document(db):
        sys.exit(1)

    print("All checks passed.")


if __name__ == "__main__":
    main()
