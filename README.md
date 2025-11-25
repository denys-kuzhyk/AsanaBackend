# AsanaBackend

Flask-based backend for the AsanaApp Android client.  
It handles:

- User authentication (login / signup / JWT refresh)
- Task management (list, create, edit, delete)
- Basic user/project context (role + current project)
- Integration with the Asana API
- Firebase / Firestore integration (via `firebase_config.py`)

---

## Tech Stack

- Language: Python 3.x  
- Framework: Flask  
- Auth: JWT (access + refresh tokens)  
- Client: Android app written in Kotlin (Jetpack Compose) using Retrofit  
- External services:
  - Asana API
  - Firebase / Firestore (via service account key)

---

## Project Structure

```
.
├── app.py             # Main Flask application / route definitions
├── asanaApi.py        # Helper functions for interacting with the Asana API
├── config.py          # Application configuration (JWT secret, Asana tokens, project IDs)
├── firebase_config.py # Firebase / Firestore configuration and initialization
├── main.py            # Entry point to run the backend (if used)
└── session.py         # Session / auth utilities (e.g. JWT helpers)

---

## Required to Run

Before starting the backend, make sure you have the following configured:

1. **Firebase / Firestore**
   - Create a Firebase project with Firestore enabled.
   - Generate a service account key in Google Cloud Console and download the JSON file.
   - Save the file as `firebase_key.json` in the project root (this file is accessed in `firebase_config.py`).
   - Do not commit this file to Git – keep it local and ensure it is listed in `.gitignore`.

2. **Application config (`config.py`)**
   - Set a JWT secret key – any strong, secret string used to sign JWT tokens.
   - Add your Asana Personal Access Token (from your Asana account) so the backend can call the Asana API.
   - Specify the Asana project GID of the project where the users are stored as tasks.

Once these values are configured and the dependencies are installed, you can start the backend server.

---

## Running Locally

1. **Clone the repository**

   ```bash
   git clone https://github.com/denys-kuzhyk/AsanaBackend.git
   cd AsanaBackend
   ```

2. **Create & activate a virtual environment (recommended)**

   ```bash
   python -m venv venv
   # macOS / Linux
   source venv/bin/activate
   # Windows
   venv\Scriptsctivate
   ```

3. **Install dependencies**

   If you have a `requirements.txt` file:

   ```bash
   pip install -r requirements.txt
   ```

   Otherwise, install the main packages you use, for example:

   ```bash
   pip install flask flask-cors flask-jwt-extended requests
   # plus any others your project requires: asana, firebase-admin, python-dotenv, etc.
   ```

4. **Configure environment / secrets**

   Depending on how you implemented `config.py`, you will typically need to set:

   - `JWT_SECRET_KEY`
   - Asana Personal Access Token
   - Asana project GID(s)
   - Path to `firebase_key.json` (if not assumed to be in the project root)

   A common pattern is to use environment variables and read them in `config.py`, or use a local `.env` file (not committed to Git).

5. **Run the app**

   For example:

   ```bash
   python app.py
   # or
   python main.py
   ```

   By default, the app usually runs on `http://127.0.0.1:5000/`.

   In the Android app, the Retrofit `BASE_URL` is set to:

   ```kotlin
   private const val BASE_URL = "http://10.0.2.2:5000/"
   ```

   `10.0.2.2` is how the Android emulator accesses your machine’s localhost.

---

## API Overview

These endpoints are consumed by the Android client via Retrofit.  
(Details here should stay in sync with the actual Flask routes.)

### Auth

#### `POST /login`

Request body:

```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

Success response (example):

```json
{
  "access_token": "<jwt>",
  "access_token_expires": 3600,
  "refresh_token": "<jwt>",
  "refresh_token_expires": 86400,
  "msg": "Logged in successfully",
  "email": "user@example.com",
  "name": "User Name",
  "id": "123456",
  "role": "Manager",
  "project_id": "proj_1,proj_2",
  "project_names": {
    "Project Name 1": "proj_1",
    "Project Name 2": "proj_2"
  }
}
```

Error response:

```json
{ "msg": "Invalid credentials" }
```

---

#### `POST /signup`

Request body (same as `/login`):

```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

Success response:

Same structure as a successful `/login` (creates a user and logs them in).

---

#### `POST /refresh`

Refreshes tokens using the refresh token.

Headers:

```text
Authorization: Bearer <refresh_token>
```

Success response:

Same structure as `/login` (new access and refresh tokens).

---

### Tasks

#### `GET /get-tasks`

Returns tasks for the given role and project.

Headers:

```text
Authorization: Bearer <access_token>
```

Query parameters:

- `role` – e.g. "Manager" or "User"
- `project_id` – current Asana project GID

Success response (example):

```json
{
  "msg": "Tasks loaded",
  "user_tasks": [
    {
      "AssigneeID": "user@example.com",
      "Status": "Open",
      "due_date": "2025-03-31",
      "name": "Task name",
      "task_id": "12345",
      "TaskDescription": "Some description"
    }
  ],
  "statuses": "Open,In Progress,Completed"
}
```

---

#### `PUT /edit-task`

Headers:

```text
Authorization: Bearer <access_token>
```

Request body:

```json
{
  "task_id": "12345",
  "due_date": "2025-03-31",
  "status": "In Progress",
  "project_id": "proj_1",
  "assignee": "user@example.com"
}
```

Response:

```json
{ "msg": "Task updated" }
```

---

#### `POST /create-task`

Headers:

```text
Authorization: Bearer <access_token>
```

Request body:

```json
{
  "due_date": "2025-03-31",
  "status": "Open",
  "project_id": "proj_1",
  "name": "New task",
  "description": "Task description",
  "assignee": "user@example.com"
}
```

Response:

```json
{ "msg": "Task created" }
```

---

#### `DELETE /delete-task`

Uses a DELETE with a JSON body.

Headers:

```text
Authorization: Bearer <access_token>
```

Request body:

```json
{ "task_id": "12345" }
```

Response:

```json
{ "msg": "Task deleted" }
```

---

### Password Management

#### `PUT /change-password`

Headers:

```text
Authorization: Bearer <access_token>
```

Request body:

```json
{
  "password": "current_password",
  "new_password": "new_strong_password"
}
```

Response:

```json
{ "msg": "Password changed successfully" }
```

---

## Git & Secrets

Make sure you do not commit secrets to the repository. At minimum, your `.gitignore` should exclude:

```gitignore
# Virtual environment
venv/
.venv/

# Firebase service account key
firebase_key.json

# Python cache
__pycache__/
*.pyc
*.pyo

# IDE files
.idea/
*.iml
```

If a secret was ever committed by mistake, rotate the key (e.g., create a new Firebase service account key) and remove the old one.

---

## Future Improvements

Some ideas for extending this backend:

- Add a formal `requirements.txt` or use Poetry / pip-tools for dependency management.
- Add unit tests (e.g. with pytest) for each endpoint.
- Add more detailed role-based access control (RBAC).
- Add CI (GitHub Actions) to run tests on each push/PR.
- Improve error handling and return more structured error codes/messages.

---

## License

You can add your preferred license here (e.g. MIT, Apache-2.0, etc.).
