# Asana Task Manager – Overview (Non‑Technical)

This project is a simple task management system built on top of **Asana**.

It consists of:

- An **Android app** (front end) that users install on their phones.
- A small **Flask backend** with **Firestore** that handles login, sessions and talking to Asana.

The goal is to let people:

- Log in on their phone
- See the tasks assigned to them
- Update task status and due dates
- (For managers) create, edit and delete tasks across projects

All while **Asana remains the main place where tasks and users are defined.**

This README is written for non‑technical readers and applies to both:

- Android app repo: `AsanaAndroidApp`
- Backend repo: `AsanaBackend`

---

## Who Is This For?

This system is designed for:

- Teams that **already use Asana** and want a simple mobile interface tailored to their workflow.
- Managers who want an easy way to:
  - See all tasks in a project
  - Assign tasks to team members
  - Create and manage tasks from their phone
- Employees who want:
  - A clean list of **only their tasks**
  - A simple way to update **status** and **due dates** on the go

It’s also a good example project for anyone interested in how an app, backend and Asana can work together.

---

## How It Works (High‑Level)

At a high level, there are three parts:

1. **Asana** – the “source of truth”
   - Asana stores:
     - The list of **users** (in a “Contact List” project)
     - The list of **tasks** (in real projects)
   - Custom fields in Asana are used to link users and tasks together.

2. **Flask backend + Firestore**
   - Checks if a user exists in Asana before allowing them to register.
   - Stores user login information and sessions in Firestore.
   - Talks to Asana’s API to read and update tasks.
   - Acts as a “middle layer” between the Android app and Asana.

3. **Android app**
   - The app the user actually sees and uses.
   - Communicates with the backend.
   - Shows tasks, user info, stats, and allows actions based on the user’s role.

Asana is where the data lives.  
The backend is the “translator”.  
The Android app is the “remote control” the user holds.

---

## Asana Setup – Contact List (Users as Tasks)

Before the system can work, you need to configure Asana in a specific way.

### 1. Create a **Contact List** project

This is a project in Asana that acts like your **user directory**.  
Each user is represented as a **task** in this project.

For this Contact List project:

- Create a **blank project** in Asana.
- For each team member, create a task (one task = one user).

In addition to the default task fields, add the following **custom fields**:

1. **Email** (Text)
   - The user’s email (this must match what they use in the Android app).
2. **Role** (Text)
   - Either `Employee` or `Manager`.
3. **Project** (Text)
   - The Asana **project GID** (ID) of the project(s) the user belongs to.
   - If the user is a **Manager**, they can have **multiple** project IDs separated by commas (no spaces).

#### Example user in Contact List

Project: **Contact List**

Task representing user:

- **Name:** John Brown  
- **Email:** `john@email.com`  
- **Role:** `Employee`  
- **Project:** `123456`

This means:
- John is an Employee.
- He belongs to the project whose Asana GID (ID) is `123456`.

---

## Asana Setup – Real Project(s) and Tasks

Next, you need one or more **real projects** where the work gets done.

### 2. Create a real Asana project (for actual tasks)

This is a normal Asana project with tasks you want your team to complete.

For each such project, add these **custom fields**:

1. **AssigneeID** (Text)
   - The **email** of the user assigned to the task.
   - This must match the Email field in the Contact List project.

2. **Status** (Single select)
   - Type: **Single‑select** custom field.
   - Options should include:  
     - `New`  
     - `Open`  
     - `In Progress`  
     - `Completed`

3. **TaskDescription** (Text)
   - A text field with additional details about the task.

#### Example task for John

Project GID: `123456` (this matches John’s Project field)

Task in that project:

- **Name:** `Do 100 push-ups`
- **AssigneeID:** `john@email.com`
- **Status:** `In Progress`
- **TaskDescription:** `Do 10 push ups every morning for 10 days.`

When the system runs successfully:

- John will see this task in the Android app.
- He’ll be able to change the **status** and **due date** (as an Employee).
- A Manager will be able to change the **assignee**, status, due date, and even delete this task.

---

## Why Users Must Exist in Asana Before Sign‑Up

The system is designed so that **Asana is the master list of allowed users**.

That means:

- You **cannot** just sign up in the Android app with any random email.
- The backend will first check the Contact List project in Asana.
- If there is no task with that email in Asana, the backend will **reject the registration**.

This has a few advantages:

- You control access **only via Asana**, by adding or editing tasks in the Contact List project.
- No one can use the app unless they were explicitly added as a user in Asana.
- Roles and project access are controlled by Asana fields (`Role`, `Project`).

So the correct order is:

1. Add the user in Asana (Contact List project).
2. Then the user can sign up in the Android app with that same email.

---

## Basic Configuration to Start the System

Once Asana is set up correctly, there’s one key step on the backend:

1. Take the **project GID** of your **Contact List project**.
2. Put it into the Flask backend configuration (`config.py`).

Along with:

- Your Asana access token (to let the backend talk to Asana)
- Firestore / Firebase configuration (for users and sessions)

After that, and once both the backend and Android app are prepared:

- You can start the backend server.
- You can install and run the Android app.
- Users can sign up and log in.

---

## Roles and What Users Can Do

There are two roles in this system, defined in Asana:

### Employee

- Sees **only their own tasks** (based on `AssigneeID = their email`).
- Can:
  - Update the **status** of their tasks.
  - Change the **due date** of their tasks.
- Cannot:
  - Create new tasks.
  - Delete tasks.
  - Reassign tasks to others.

### Manager

- Sees **all tasks** in the current project.
- Can:
  - Edit **status**, **due date**, and **assignee** of tasks.
  - **Create** new tasks.
  - **Delete** any task in the project.
- From the **Home** screen:
  - Can switch between different projects (if multiple project IDs are assigned in the Contact List).

---

## Example User Flow

Here is what the whole process looks like for a new user.

### 1. Manager sets up John in Asana

In the **Contact List** project:

- Task created with:  
  `Name = John Brown`, `Email = john@email.com`,  
  `Role = Employee`, `Project = 123456`.

In real project `123456`:

- Task created:  
  `Name = Do 100 push-ups`,  
  `AssigneeID = john@email.com`,  
  `Status = In Progress`,  
  `TaskDescription = Do 10 push ups every morning for 10 days.`

### 2. John opens the Android app

- John sees the **Login** screen.
- He taps **Sign Up**.

### 3. Sign Up

- John enters his email and password.
- The backend checks Asana:
  - Looks in the Contact List project for a task with email `john@email.com`.
  - Finds John’s record and role (Employee).
- The backend creates John’s user record in Firestore and allows registration.

### 4. After login

In the Android app:

- John logs in with his email and password.
- On the **Home** screen, he sees:
  - Basic stats (number of tasks).
  - Buttons to go to **Account** and **Tasks**.
- In **Account**, he can see his:
  - ID, name, email, role.
  - Option to change password.
- In **Tasks**, he sees:
  - Only tasks where `AssigneeID = john@email.com`.
  - Including **“Do 100 push-ups”**.
- John can:
  - Change the task **status** (for example, from *In Progress* to *Completed*).
  - Change the **due date**.

A Manager user would see all tasks in the project, could create new tasks, and could reassign any task.

---

## Getting Started – Summary (Non‑Technical Checklist)

1. **In Asana – Contact List**
   - Create a project for users.
   - For each user, create a task with:
     - `Email`
     - `Role` (`Employee` or `Manager`)
     - `Project` (one or more Asana project IDs)

2. **In Asana – Real Project(s)**
   - For each real project:
     - Add custom fields:
       - `AssigneeID` (Text)
       - `Status` (Single select: New, Open, In Progress, Completed)
       - `TaskDescription` (Text)
     - Create tasks and fill in these fields.

3. **In the backend (Flask + Firestore)**
   - Configure:
     - Contact List project GID
     - Asana access token
     - Firebase / Firestore credentials
   - Start the backend server.

4. **In the Android app**
   - Make sure the app points to the correct backend URL.
   - Install and run the app on a device or emulator.

5. **User registration**
   - Only users already present in the Asana Contact List can sign up.
   - Once registered, users can log in and manage their tasks.

---

## Limitations & Scope

This project is intentionally simple. It:

- Is **not** an official Asana product.
- Focuses on:
  - Simple projects
  - Basic tasks
  - A small set of custom fields
- Does **not** currently handle:
  - Subtasks
  - Attachments
  - Comments
  - Multiple workspaces or complex Asana configurations
- Depends heavily on:
  - Asana custom fields being named and configured exactly as described.
  - Users being created first in the Asana Contact List project.

It is ideal as:

- A learning project
- A small internal tool
- A demonstration of how mobile + backend + Asana can fit together

---

## Future Ideas

Possible directions to extend the system:

- **Push notifications** when:
  - New tasks are assigned
  - Task status changes
- **Better filtering and search** in the Android app:
  - By status
  - By due date
- **Richer Asana integration**:
  - Subtasks
  - Attachments
  - Comments
- **In‑app user management** for managers:
  - Instead of only managing users via Asana Contact List
- **Multi‑workspace support** and more advanced permissions

---

## Repositories

This system is split into two repositories:

- **Backend (Flask + Firestore + Asana integration)**  
  [Repository](https://github.com/denys-kuzhyk/AsanaBackend)

- **Android app (Kotlin + Jetpack Compose)**  
  [Repository](https://github.com/denys-kuzhyk/AsanaAndroidApp)

