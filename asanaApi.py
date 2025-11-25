import asana
from asana.rest import ApiException
from app import app


configuration = asana.Configuration()
configuration.access_token = app.config["ASANA_ACCESS_TOKEN"]
api_client = asana.ApiClient(configuration)

projects_api_instance = asana.ProjectsApi(api_client)
tasks_api_instance = asana.TasksApi(api_client)

# ID of the project where all the users are stored
USERS_PROJECT_ID = app.config["USERS_PROJECT_ID"]

# Custom name of the status column in the projects
STATUS_COLUMN_NAME = app.config["STATUS_COLUMN_NAME"]

# Currently, there can be two types of roles
# a Manager (the one who oversees the projects assigned to them)
# an Employee (the one who is under the Manager and sees only the tasks assigned to them in one specific project)
ROLE_NAMES = app.config["ROLE_NAMES"]

#Names of custom columns in Asana's users list (project where all users are stored)
CUSTOM_NAMES = app.config["CUSTOM_NAMES"]


# get the list of project IDs (if it's a Manager) or a single project ID (if it's an Employee) from Asana
def get_user_project_column(email):

    opts = {
        'project': USERS_PROJECT_ID,
        'opt_fields': 'custom_fields'
    }


    response = tasks_api_instance.get_tasks(opts)

    for data in response:

        #looking for the Email column
        for column in data['custom_fields']:
            if column['name'] == CUSTOM_NAMES["email"]:  #found the Email column
                if column['text_value'] == email:  #comparing the value in this column to the input

                    for column2 in data['custom_fields']:  #looking for the Project column
                        if column2['name'] == CUSTOM_NAMES['project']:  #found the Project column

                            return column2['text_value']  #returning the value

    return "400"


# takes all custom statuses of tasks and their IDs in Asana in a specific project
def get_status_ids(project_id):

    opts = {
        'opt_fields': "custom_field_settings,custom_field_settings.custom_field"
    }

    api_response = projects_api_instance.get_project(project_id, opts)


    statuses = {} # for all custom statuses of the project
    status_field_id = "" # for the ID of the status column

    for column in api_response['custom_field_settings']: # looking for the status column
        if column['custom_field']['name'] == STATUS_COLUMN_NAME: # found the status column
            statuses = column['custom_field']['enum_options'] # assigning a dictionary with all custom statuses to a variable
            status_field_id = column['custom_field']['gid'] # adding 'id' key with the value of the ID of the status column


    statuses_clean = {} # for final data return


    for status in statuses:
        statuses_clean[status['name']] = status['gid'] # getting rid of all unnecessary data and leaving only status name and its ID

    statuses_clean['id'] = status_field_id # adding the ID of the status column to the final return data

    return statuses_clean


def get_user_data(email): # for getting user data from the Users project in Asana upon sign up

    opts = {
        'project': USERS_PROJECT_ID,  # str | The project to filter tasks on.
        'opt_fields': 'name,custom_fields'
    }

    response = tasks_api_instance.get_tasks(opts)


    return_data = {}


    for user in response: # looking for user's record
        for column in user['custom_fields']:
            if column['name'] == CUSTOM_NAMES['email']: # found the email column
                if column['text_value'] == email: # found the user

                    for column1 in user['custom_fields']: # looking for the custom role column
                        if column1['name'] == CUSTOM_NAMES['role']: # found it
                            return_data['role'] = column1['text_value']

                    #taking the user ID (Asana task ID) and their name
                    return_data['id'] = user['gid']
                    return_data['name'] = user['name']


                    return return_data

    return '401'

# for Managers - getting the project IDs and their names to further display them on the Home screen in a Dropdown field
def get_project_names(project_ids):

    # project_ids is a string with one or more IDs separated by a comma
    # remaking it into a list
    project_ids = project_ids.split(",")

    return_data = {}

    # going through each project ID and taking its name
    for project in project_ids:

        opts = {
            'opt_fields': 'name'
        }


        response = projects_api_instance.get_project(project, opts)
        # assigning every project name a project ID - {project name: project ID}
        return_data[response['name']] = project

    return return_data


# for Employees - getting all tasks to which the user is assigned
def get_employee_tasks(email, project_id):


    opts = {
        'project': project_id,
        'opt_fields': 'name,due_on,custom_fields,description'
    }

    response = tasks_api_instance.get_tasks(opts)

    tasks = []
    # going through each task in the project
    for data in response:

        for column in data['custom_fields']: # looking for the assignee column
            if column['name'] == CUSTOM_NAMES['assignee']: # found the assignee column
                if column['text_value'] == email: # found a task assigned to this user
                    tasks.append(data) # adding this task to the list of tasks

    clean_tasks = [] # preparing for final data return

    for task in tasks:

        # mapping default Asana columns
        ready_task = {'task_id': task['gid'], 'due_date': task['due_on'], 'name': task['name']}


        # mapping custom columns
        for column in task['custom_fields']:
            ready_task[column['name']] = column['display_value']

        clean_tasks.append(ready_task) # adding this task to the final list of tasks only with necessary data

    return clean_tasks


# for Managers - getting all tasks that exist in a specific project
def get_manager_tasks(project_id):

    opts = {
        'project': project_id,
        'opt_fields': 'name,due_on,custom_fields,description'
    }

    response = tasks_api_instance.get_tasks(opts)

    tasks = []

    for data in response: # going through each task and adding it to the list

        tasks.append(data)

    clean_tasks = []  # preparing for final data return

    for task in tasks:

        # mapping default Asana columns
        ready_task = {'task_id': task['gid'], 'due_date': task['due_on'], 'name': task['name']}

        # mapping custom columns
        for column in task['custom_fields']:
            ready_task[column['name']] = column['display_value']

        clean_tasks.append(ready_task) # adding this task to the final list of tasks only with necessary data

    return clean_tasks


# getting the ID of the custom assignee column in a specific project
def get_assignee_column(project_id):
    opts = {
        'opt_fields': 'custom_field_settings,custom_field_settings.custom_field'
    }

    response = projects_api_instance.get_project(project_id, opts)

    assignee_column = ""
    for column in response['custom_field_settings']: # looking for the custom assignee column
        if column['custom_field']['name'] == CUSTOM_NAMES["assignee"]: # found the assignee column
            assignee_column = column['custom_field']['gid']

    return assignee_column


# editing a task - for both roles
def edit_task(task_id, due_date, status, project_id, assignee):

    # getting status IDs for further value assignment in the custom status column
    status_ids = get_status_ids(project_id)
    # getting the ID of the custom assignee column
    assignee_column = get_assignee_column(project_id)

    body = {"data": {"due_on": due_date, "custom_fields" : {status_ids['id']: status_ids[status], assignee_column: assignee}}}

    try:
        # updating the task in Asana
        tasks_api_instance.update_task(body, task_id, {})

        return "Task edited successfully"

    except ApiException as e:
        return "Exception when calling ProjectsApi->get_project: %s\n" % e


# getting the custom column names and their IDs for a specific project - for Managers
def get_custom_columns(project_id):

    opts = {
        'opt_fields': "custom_field_settings,custom_field_settings.custom_field"
    }

    api_response = projects_api_instance.get_project(project_id, opts)

    custom_columns = {}

    # only the description and the assignee columns are needed - for further use in task creation by Manager
    assignee_column = get_assignee_column(project_id) # for assignee column, we can use an already created function

    for data in api_response["custom_field_settings"]:
        if data['custom_field']['name'] == CUSTOM_NAMES['description']:
            custom_columns[CUSTOM_NAMES['description']] = data['custom_field']['gid']
            custom_columns[CUSTOM_NAMES['assignee']] = assignee_column

    return custom_columns


# creating a task - for Managers
def create_task(project_id, due_date, status, name, description, assignee):

    # getting the IDs of statuses in this project
    status_ids = get_status_ids(project_id)
    # getting the IDs and the names of custom columns needed for task creation (description and assignee)
    column_names = get_custom_columns(project_id)

    body = {
        "data": {
            "projects": [project_id],
            "due_on": due_date,
            "name": name,
            "custom_fields" : {
                status_ids['id']: status_ids[status],
                column_names[CUSTOM_NAMES['assignee']]: assignee,
                column_names[CUSTOM_NAMES['description']]: description
            }
        }
    }

    try:
        tasks_api_instance.create_task(body, {})

        return "Task created successfully"

    except ApiException as e:
        return "Exception when calling TasksApi->create_task: %s\n" % e


# deleting a task - for Managers
def delete_task(task_id):
    try:

        tasks_api_instance.delete_task(task_id)

        return "Task deleted successfully"

    except ApiException as e:
        return "Exception when calling TasksApi->delete_task: %s\n" % e


