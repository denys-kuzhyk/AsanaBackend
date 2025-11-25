JWT_SECRET_KEY = "<YOUR_SECRET_KEY>"
JWT_ACCESS_TOKEN_EXPIRES = 30
JWT_REFRESH_TOKEN_EXPIRES = 45

# NAMES OF THE CUSTOM ROLE NAMES IN ASANA. PREFERRED TO STAY AS IS (SOME FUNCTIONALITY MAY NOT WORK IF THEY ARE DIFFERENT)
ROLE_NAMES = {
    "inferior": "Employee",
    "superior": "Manager"
}

ASANA_ACCESS_TOKEN = "<YOUR_ASANA_ACCESS_TOKEN>"

USERS_PROJECT_ID = "<ID OF THE PROJECT WHERE THE USERS ARE STORED>"

# NAME OF THE CUSTOM STATUS COLUMN IN ASANA
STATUS_COLUMN_NAME = "Status"

# NAMES OF THE CUSTOM COLUMNS IN ASANA
CUSTOM_NAMES = {
    "assignee": "AssigneeID",
    "status": "Status",
    "email": "Email",
    "project": "Project",
    "description": "TaskDescription",
    "role": "Role",
    "id": "ID",
    "name": "Name"
}
