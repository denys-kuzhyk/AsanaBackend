import asanaApi
from firebase_config import db, get_user_email_with_id
from session import create_session_and_tokens, revoke_session
import random
import bcrypt
from app import app
from flask import Flask, request, jsonify
from flask_jwt_extended import  JWTManager, jwt_required, get_jwt_identity, \
    get_jwt
from asanaApi import get_employee_tasks, get_user_data, \
    get_manager_tasks, get_status_ids, get_project_names, get_user_project_column



# app = Flask(__name__)
# app.config.from_pyfile("config.py")

ROLE_NAMES = app.config["ROLE_NAMES"]


jwt = JWTManager(app)


# creating a new user in Firestore
def add_user(user_data: dict):
    user_id = str(user_data["id"])  # document name must be string
    user_ref = db.collection("users").document(user_id)
    user_ref.set(user_data)


# hashing a password
def hash_password(plain_password):
    salt = bcrypt.gensalt()

    hashed = bcrypt.hashpw(plain_password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


# comparing a plain password with a hashed version
def check_password(plain_password, hashed_password):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


@app.route("/signup", methods=["POST"])
def signup():

    email = request.json.get("email")
    password = request.json.get("password")

    hashed_password = hash_password(password)

    # checking whether such user exists
    try:

        query_email = db.collection('users').where(field_path='email', op_string='==', value=email)
        result_email = list(query_email.stream())

    except Exception as e:
        return jsonify({"msg": e}), 500

    #if they don't
    if len(result_email) == 0:

        try:

            # getting user data from Asana
            user_data = get_user_data(email)

            # if this user is present in Asana
            if user_data != "401":

                # collecting all necessary data
                user_id = user_data['id']
                user_name = user_data['name']
                user_role = user_data['role']

                project_list = get_user_project_column(email)

                # generating session id
                session_id = random.randint(100000000, 999999999)

                # adding the user to Firestore
                add_user({
                    "name": user_name,
                    "password": hashed_password,
                    "id": user_id,
                    "email": email,
                    "role": user_role
                })

                # creating a new session for the user
                session_data = create_session_and_tokens(str(user_id), str(session_id))
                session_data["msg"] = "User created successfully"
                session_data['name'] = user_name
                session_data['email'] = email
                session_data['id'] = user_id
                session_data['role'] = user_role
                session_data['project_id'] = project_list # list of projects assigned to the user

                session_data['project_names'] = get_project_names(project_list)

                return jsonify(session_data), 200

            else:
                return jsonify({'msg': 'User with such email is not in the system'}), 401



        except Exception as e:
            return jsonify({"msg": e}), 500

    # if it does
    else:
        msg = "User with such credentials already exists"

        return jsonify({'msg': msg}), 409


@app.route("/login", methods=["POST"])
def login():


    email = request.json.get("email")
    password = request.json.get("password")

    #checking whether such user exists in Firestore already
    try:
        query_email = db.collection('users').where(field_path='email', op_string='==', value=email)
        result_email = list(query_email.stream())

    except Exception as e:
        return jsonify({"msg": e}), 500


    #if it doesn't
    if len(result_email) == 0:
        return jsonify({"msg": "Invalid credentials"}), 401

    #if it does
    else:
        # collecting user data
        user_id = result_email[0].to_dict()['id']
        user_name = result_email[0].to_dict()['name']
        user_role = result_email[0].to_dict()['role']

        try:
            project_list = get_user_project_column(email)

            # checking the password
            hashed_password = result_email[0].to_dict()['password']

            check_password(password, hashed_password)

            if check_password(password, hashed_password):

                # creating session
                session_id = random.randint(100000000, 999999999)

                session_data = create_session_and_tokens(str(user_id), str(session_id))
                session_data["msg"] = "User logged in successfully"
                session_data['name'] = user_name
                session_data['email'] = email
                session_data['id'] = user_id
                session_data['role'] = user_role
                session_data['project_id'] = project_list


                session_data['project_names'] = get_project_names(project_list)

                return jsonify(session_data), 200

            else:
                return jsonify({"msg": "Invalid credentials"}), 401

        except Exception as e:
            return jsonify({"msg": e}), 500


@app.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():

    identity = get_jwt_identity()  # taking the user ID
    claims = get_jwt()
    session_id = claims.get("session_id") # taking the session ID

    try:
        # checking if the session is revoked
        revoked = db.collection("sessions").document(session_id).get().to_dict().get("revoked")

    except Exception as e:
        return jsonify({"msg": e}), 500

    if not revoked:

        try:
            # revoking the current session
            revoke_session(session_id)

            # generating new session id
            new_session_id = random.randint(100000000, 999999999)

            # creating new session in Firestore
            return_data = create_session_and_tokens(identity, str(new_session_id))

            return_data["msg"] = "Token refreshed successfully"


            return jsonify(return_data), 200

        except Exception as e:
            return jsonify({"msg": e}), 500

    else:
        return jsonify({"msg": "Token is not valid anymore"}), 401


# Not currently used by the app. Planning to add this in the future
@app.route("/signout", methods=["PUT"])
@jwt_required()
def signout():

    claims = get_jwt()
    session_id = claims.get("session_id") # taking the session ID

    # revoking the session
    try:
        revoked = db.collection("sessions").document(session_id).get().to_dict().get("revoked")

        if not revoked:

            revoke_session(session_id)

            return jsonify({"msg": "User signed out successfully"}), 200

        else:
            return jsonify({"msg": "Token is not valid anymore"}), 401

    except Exception as e:
        return jsonify({"msg": e}), 500


@app.route("/get-tasks", methods=["GET"])
@jwt_required()
def get_tasks():
    user_id = get_jwt_identity() # taking the user ID
    claims = get_jwt()
    session_id = claims.get("session_id") # taking the session ID

    role = request.args.get("role")
    project_id = request.args.get("project_id")

    # checking if the session is revoked
    try:
        revoked = db.collection("sessions").document(session_id).get().to_dict().get("revoked")
    except Exception as e:
        return jsonify({"msg": e}), 500


    if revoked:
        return jsonify({"msg": "Token is not valid anymore"}), 401

    else:

        try:

            # getting the statuses, but without the custom status ID, since we don't need it here
            statuses = get_status_ids(project_id)
            statuses.pop("id")

            # remaking the statuses into a string separated by a comma
            statuses_string = ""
            for key in statuses:
                statuses_string += f"{key},"

            statuses_string = statuses_string[:-1] # removing the comma at the end

            if role == ROLE_NAMES["inferior"]: # if it's an Employee, we use functions for Employees

                user_email = get_user_email_with_id(user_id)
                tasks = get_employee_tasks(email=user_email, project_id=project_id)

                return jsonify({"user_tasks": tasks, "statuses": statuses_string, "msg": "Tasks downloaded successfully"}), 200

            elif role == ROLE_NAMES["superior"]: # if it's a Manager - function for Managers

                tasks = get_manager_tasks(project_id=project_id)

                return jsonify({"user_tasks": tasks, "statuses": statuses_string, "msg": "Tasks downloaded successfully"}), 200

        except Exception as e:
            return jsonify({"msg": e}), 500


@app.route("/edit-task", methods=["PUT"])
@jwt_required()
def edit_task():

    claims = get_jwt()
    session_id = claims.get("session_id") # getting session ID

    try:
        revoked = db.collection("sessions").document(session_id).get().to_dict().get("revoked")
    except Exception as e:
        return jsonify({"msg": e}), 500

    task_id = request.json.get("task_id")
    due_date = request.json.get("due_date")
    status = request.json.get("status")
    project_id = request.json.get("project_id")
    assignee = request.json.get("assignee")

    if revoked:
        return jsonify({"msg": "Token is not valid anymore"}), 401

    else:

        # if the session is not revoked - use the edit_task function to edit a specific task
        try:
            result = asanaApi.edit_task(task_id, due_date, status, project_id, assignee)

        except Exception as e:
            return jsonify({"msg": e}), 500


        if result == "Task edited successfully":
            return jsonify({'msg': 'Task edited successfully'}), 200

        else:
            return jsonify({'msg': result}), 500


@app.route("/create-task", methods=["POST"])
@jwt_required()
def create_task():
    claims = get_jwt()
    session_id = claims.get("session_id") # taking the session ID

    try:
        revoked = db.collection("sessions").document(session_id).get().to_dict().get("revoked")

    except Exception as e:
        return jsonify({"msg": e}), 500

    due_date = request.json.get("due_date")
    status = request.json.get("status")
    project_id = request.json.get("project_id")
    name = request.json.get("name")
    description = request.json.get("description")
    assignee = request.json.get("assignee")


    if revoked:
        return jsonify({"msg": "Token is not valid anymore"}), 401

    else:
        # if the session is not revoked - use create_task function to create a task in a specific project
        try:
            result = asanaApi.create_task(
                project_id=project_id,
                due_date=due_date,
                status=status,
                name=name,
                description=description,
                assignee=assignee
            )

        except Exception as e:
            return jsonify({"msg": e}), 500


        if result == "Task created successfully":
            return jsonify({'msg': 'Task created successfully'}), 200

        else:
            return jsonify({'msg': result}), 500


@app.route("/delete-task", methods=["DELETE"])
@jwt_required()
def delete_task():
    claims = get_jwt()
    session_id = claims.get("session_id") # taking the session ID

    try:
        revoked = db.collection("sessions").document(session_id).get().to_dict().get("revoked")

    except Exception as e:
        return jsonify({"msg": e}), 500


    task_id = request.json.get("task_id")

    if revoked:
        return jsonify({"msg": "Token is not valid anymore"}), 401

    else:
        # if the session is not revoked = using the delete_task function to delete a specific task
        try:
            result = asanaApi.delete_task(task_id)

        except Exception as e:
            return jsonify({"msg": e}), 500

        if result == "Task deleted successfully":
            return jsonify({'msg': 'Task deleted successfully'}), 200

        else:
            return jsonify({'msg': result}), 500


@app.route("/change-password", methods=["PUT"])
@jwt_required()
def change_password():
    user_id = get_jwt_identity() # taking the user ID
    claims = get_jwt()
    session_id = claims.get("session_id") # taking the session ID

    try:
        revoked = db.collection("sessions").document(session_id).get().to_dict().get("revoked")

    except Exception as e:
        return jsonify({"msg": e}), 500


    if revoked:
        return jsonify({"msg": "Token is not valid anymore"}), 401

    else:
        # if the session is not revoked - we check the input with the password stored in Firestore
        try:
            query = db.collection('users').where(field_path='id', op_string='==', value=user_id)
            result = list(query.stream())

            # taking the data from the request
            password = request.json.get("password")

            # checking the password
            hashed_password = result[0].to_dict()['password']

            matches = check_password(password, hashed_password)

            # if the passwords match - we set a password provided by the user as the new password
            if matches:

                new_password = request.json.get("new_password")

                new_password_hashed = hash_password(new_password)

                db.collection('users').document(user_id).update(
                    {
                        'password': new_password_hashed
                    }
                )

                return jsonify({'msg': 'Password updated successfully'}), 200

            else:
                return jsonify({"msg": "Invalid password"}), 401

        except Exception as e:
            return jsonify({"msg": e}), 500


app.run(debug=True)







