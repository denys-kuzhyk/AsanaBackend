# AsanaBackend

Flask-based backend for the **AsanaApp** Android client.  
It handles:

- User authentication (login / signup / JWT refresh)
- Secure token storage (access & refresh tokens)
- Task management (list, create, edit, delete)
- Simple user & project context (role + current project)
- Optional Firebase configuration for push notifications (via `firebase_config.py`)

---

## Tech Stack

- **Language:** Python 3.x  
- **Framework:** Flask  
- **Auth:** JWT (access + refresh tokens)  
- **Client:** Android app written in Kotlin (Jetpack Compose) using Retrofit  
- **Other:** Asana API helpers (`asanaApi.py`), optional Firebase config

---

## Project Structure

```text
.
├── app.py             # Main Flask application / route definitions
├── asanaApi.py        # Helper functions for interacting with Asana API
├── config.py          # Configuration (tokens, base URLs, etc.)
├── firebase_config.py # Firebase-related config/helpers (no secrets committed)
├── main.py            # Optional entry-point to run the app
└── session.py         # Session / auth utilities (JWT, etc.)

## Required to Run

Before starting the backend, make sure you have the following configured:

1. **Firebase / Firestore**
   - Create a **Firebase project** with **Firestore** enabled.
   - Generate a **service account key** in Google Cloud Console and download the JSON file.
   - Save the file as `firebase_key.json` in the project root (this file is read in `firebase_config.py`).
   - **Do not commit this file to Git** – keep it local and add it to `.gitignore`.

2. **Application config (`config.py`)**
   - Set a `JWT_SECRET_KEY` – any strong, secret string used to sign JWT tokens.
   - Add your **Asana Personal Access Token** (from your Asana account) so the backend can call the Asana API.
   - Specify the **Asana project GID** of the project where users are stored as tasks.

Once these values are configured and the dependencies are installed, you can start the backend server.
