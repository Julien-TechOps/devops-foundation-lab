# Local Python Environment Setup — DevOps Foundation Lab

## Objective

Prepare the local Python development environment inside the project repository.

This step is not about deploying the application on the VM.
It is about storing the application source code in the repository and making the local development environment usable in WSL and VS Code.

---

## Why this step matters

At first, the application only existed on the remote VM (`app-01`).

That is not enough for a real project.

The source code must also exist in the repository because:

- the repository must become the source of truth
- the code must be versioned
- the project must be reproducible
- future automation (Ansible, CI/CD, Docker) depends on the repository content

---

## Initial situation

At this stage, the following files may exist but still be empty:

- `app/src/app.py`
- `app/requirements.txt`

This was the case in the project before copying the MVP code from the VM into the repository.

---

## Target structure

app/
├── .venv/
├── requirements.txt
├── src/
│   ├── app.py
│   ├── db.py
│   └── templates/
└── tests/

## Step 1 — Go to the application directory

    cd ~/devops-foundation-lab/app

## Step 2 — Create a local virtual environment

    python3 -m venv .venv

Why :
A virtual environment isolates project dependencies from the rest of the system.
This avoids conflicts between projects and ensures better reproducibility.

## Step 3 — Activate the virtual environment

    source .venv/bin/activate

Expected result: (.venv)

appears at the beginning of the shell prompt.

## Step 4 — Fill requirements.txt

Edit the file:

    nano requirements.txt

Content:

    flask
    pymysql

Why :
This file declares the Python dependencies required by the MVP application.

    flask is used to build the web application
    pymysql is used to connect Python to MariaDB

## Step 5 — Install dependencies locally

pip install -r requirements.txt

Why :
This installs the exact dependencies declared in the project.

## Step 6 — Copy the application source code into the repository

Edit:

    nano src/app.py

Example MVP code:

    from flask import Flask, request
    import pymysql


#Create the Flask application
app = Flask(__name__)

#Database connection settings
#For now, values are hardcoded because this is still the manual MVP phase.
#Later, they should be moved to environment variables.
DB_HOST = "192.168.1.43"
DB_USER = "app_user"
DB_PASSWORD = "password"
DB_NAME = "app_db"


@app.route("/", methods=["GET"])
def form():
    """
    Display a very simple HTML form.
    This is the entry point of the MVP.
    """
    return """
        <h2>DevOps Foundation Lab</h2>
        <form method="POST" action="/submit">
            First name: <input name="first_name"><br><br>
            Last name: <input name="last_name"><br><br>
            <input type="submit" value="Send">
        </form>
    """


 app.route("/submit", methods=["POST"])
def submit():
    """
    Receive form data and insert it into the MariaDB database.
    """
    first_name = request.form["first_name"]
    last_name = request.form["last_name"]

    conn = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )

    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (first_name, last_name) VALUES (%s, %s)",
        (first_name, last_name)
    )

    conn.commit()
    conn.close()

    return "User added!"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)


Why : 
The MVP code must live in the repository, not only on the VM.

## Step 7 — Configure VS Code with the correct interpreter

In VS Code:

Open the command palette
Select Python: Select Interpreter
Choose Enter Interpreter Path
Select:
/home/julien/devops-foundation-lab/app/.venv/bin/python

Why : 
VS Code must use the local virtual environment to resolve imports correctly.
Without that, modules such as flask or pymysql may appear as missing even if the code is correct.

## Step 8 — Verify the environment

In the terminal:

    which python

Expected result: /home/julien/devops-foundation-lab/app/.venv/bin/python

You can also verify installed packages:

    pip list

Expected packages include:

Flask
PyMySQL

# Validation Checklist
 .venv created
 virtual environment activated
 requirements.txt filled
 dependencies installed
 app/src/app.py filled with the MVP code
 VS Code configured with .venv/bin/python
 imports resolved correctly in the editor


# Key Learning Points
Why not keep the code only on the VM?
Because a VM is an execution target, not the source of truth.

Why version requirements.txt?
Because the environment must be reproducible.

Why use a virtual environment locally if the app already runs on the VM?
Because local development and repository consistency matter just as much as runtime execution.

# Limits of this stage

This step does not yet include:

environment variables
application packaging
service management
automated deployment
production-grade configuration

This is still part of consolidating the MVP.