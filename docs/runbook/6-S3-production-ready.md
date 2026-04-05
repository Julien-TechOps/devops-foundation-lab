# 6 - Sprint 3 Production Readiness

## Goal
Move the lab from the end-of-sprint-2 state to a more reliable sprint-3 state where the application is managed as a service, configured through variables, and deployed in a cleaner, repeatable way.

## Starting Point
At the end of sprint 2:

- VMs are reachable with SSH
- MariaDB is installed and configured on `db-01`
- the database schema is applied
- the Flask application is deployed with Ansible
- the full stack can be deployed with `playbooks/site.yml`

Sprint 3 does not introduce a new business feature.
It improves runtime reliability, configuration management, and deployment quality.

---

## Why
At this stage, the application works, but the deployment is still fragile:

- process lifecycle is not managed by the operating system
- some configuration can drift between files
- file paths and deployment logic can become inconsistent
- "service is running" is not enough to guarantee the application really works

Sprint 3 focuses on making the deployment closer to a production-style setup.

---

## Step 1 - Confirm the sprint 2 baseline

Before changing the deployment model, make sure the sprint 2 stack is still healthy:

    ansible-playbook -i inventory/dev/hosts.ini playbooks/site.yml

Then verify:

    ssh app-01
    systemctl status flask-user-app

    ssh db-01
    sudo mysql app_db -e "SHOW TABLES;"

Expected result:

- the playbook completes without fatal errors
- the `users` table exists in `app_db`
- the application host is reachable

Why:

- sprint 3 should improve an already working baseline
- debugging is easier when infrastructure state is known before changes

---

## Step 2 - Centralize configuration in inventory variables

Create or update:

    inventory/dev/group_vars/all.yml

Example:

    app_name: flask-user-app
    app_dir: /opt/app
    app_user: appuser
    app_group: appuser

    app_port: 5000
    flask_env: development

    db_host: 192.168.1.43
    db_name: app_db
    db_user: app_user
    db_password: app_password

Why:

- creates a single source of truth for the application deployment
- avoids hardcoded values spread across roles, templates, and source code
- makes environment-specific inventory easier to manage later

Validation:

    ansible-inventory -i inventory/dev/hosts.ini --host app-01

Expected result:

- `app_name`
- `app_dir`
- `app_user`
- `app_group`
- `db_host`
- `db_name`
- `db_user`
- `db_password`

must all appear in the resolved host variables.

---

## Step 3 - Update the application code for sprint 3

Sprint 3 requires a new application version.
The code must be provided explicitly because the user cannot infer:

- the new imports
- the environment-variable based configuration
- the use of `render_template("index.html")`
- the required location of the HTML template

Replace `app/src/app.py` with:

```python
import os
from flask import Flask, render_template, request, redirect
import pymysql

app = Flask(__name__)

DB_HOST = os.environ["DB_HOST"]
DB_NAME = os.environ["DB_NAME"]
DB_USER = os.environ["DB_USER"]
DB_PASSWORD = os.environ["DB_PASSWORD"]
APP_PORT = int(os.environ.get("APP_PORT", "5000"))

def get_connection():
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        cursorclass=pymysql.cursors.Cursor
    )

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]

        connection = get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO users (first_name, last_name) VALUES (%s, %s)",
                    (first_name, last_name)
                )
            connection.commit()
        finally:
            connection.close()

        return redirect("/")

    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=APP_PORT)
```

Create the directory and template file:

    mkdir -p app/src/templates

Create `app/src/templates/index.html` with:

<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>User Registration</title>
</head>
<body>
  <h1>User Registration</h1>

  <form method="POST" action="/">
    <div>
      <label for="first_name">First name</label>
      <input type="text" id="first_name" name="first_name" required />
    </div>

    <div>
      <label for="last_name">Last name</label>
      <input type="text" id="last_name" name="last_name" required />
    </div>

    <div>
      <button type="submit">Submit</button>
    </div>
  </form>
</body>
</html>


Why:

- the application now depends on environment variables instead of hardcoded database settings
- `render_template("index.html")` requires a real template file on disk
- Flask expects templates in `app/src/templates/` in this project structure

Validation:

Check that both files exist:

    ls app/src/app.py
    ls app/src/templates/index.html

Expected result:

- `app/src/app.py` exists with the sprint 3 code
- `app/src/templates/index.html` exists before Ansible deployment

---

## Step 4 - Generate the runtime environment file

Create the environment template in:

    roles/app/templates/app.env.j2

Example:

    DB_HOST={{ db_host }}
    DB_NAME={{ db_name }}
    DB_USER={{ db_user }}
    DB_PASSWORD={{ db_password }}
    APP_PORT={{ app_port }}
    FLASK_ENV={{ flask_env }}

Why:

- application configuration becomes environment-driven
- the same code can be reused across environments
- credentials are no longer embedded in source files

Expected result:

- the application starts only if required environment variables are present
- Ansible becomes responsible for generating runtime configuration

---

## Step 5 - Replace ad hoc runtime with systemd

The application should no longer depend on a manual command, `nohup`, or an interactive shell.

Create:

    roles/app/templates/flask-app.service.j2

Example:

    [Unit]
    Description=Flask User App
    After=network.target

    [Service]
    User={{ app_user }}
    Group={{ app_group }}
    WorkingDirectory={{ app_dir }}
    EnvironmentFile={{ app_dir }}/app.env
    ExecStart={{ app_dir }}/.venv/bin/python {{ app_dir }}/app.py
    Restart=always
    RestartSec=5

    [Install]
    WantedBy=multi-user.target

Why:

- systemd manages startup, restart, and logs
- the service starts automatically after reboot
- failures become observable with native Linux tooling

Validation on `app-01`:

    sudo systemctl daemon-reload
    sudo systemctl status flask-user-app
    sudo journalctl -u flask-user-app -n 50

Expected result:

- service is `active (running)`
- logs are available through `journalctl`
- the service restarts automatically after failure or reboot

---

## Step 6 - Clean the application role

The `app` role should deploy the application in a predictable order:

1. create the application group
2. create the application user
3. create the application directory
4. copy `app.py`
5. copy `requirements.txt`
6. copy HTML templates
7. create the virtual environment
8. install Python dependencies
9. deploy `app.env`
10. deploy the systemd unit
11. enable and start the service

The role should use the real project structure:

    app/src/app.py
    app/src/templates/
    app/requirements.txt

Why:

- deployment logic stays aligned with the repository layout
- tasks become easier to read and debug
- service restarts happen only when relevant files change

Expected result:

- the role becomes easier to re-run safely
- source code, config, and service definition are deployed consistently

---

## Step 7 - Add handlers for service lifecycle

Define handlers in:

    roles/app/handlers/main.yml

Example:

    - name: Reload systemd
      ansible.builtin.systemd:
        daemon_reload: true

    - name: Restart app service
      ansible.builtin.systemd:
        name: "{{ app_name }}"
        state: restarted

Why:

- service restarts should happen only when deployment changes require it
- `daemon_reload` is required after updating a unit file
- handlers improve idempotence and reduce unnecessary restarts

---

## Step 8 - Deploy sprint 3 changes

Run:

    ANSIBLE_LOCAL_TEMP=/tmp/ansible-local ANSIBLE_REMOTE_TEMP=/tmp/ansible-remote ansible-playbook -i inventory/dev/hosts.ini playbooks/site.yml

Why this command:

- some environments cannot write to the default `~/.ansible/tmp`
- explicitly using `/tmp` avoids local temp directory issues

Expected result:

- the playbook completes successfully
- the app service is enabled and started
- no manual SSH deployment step is required

---

## Step 9 - Validate the application end to end

Check the service:

    ssh app-01
    systemctl status flask-user-app

Check the rendered environment file:

    sudo cat /opt/app/app.env

Test the HTTP endpoint from your workstation:

    curl http://192.168.1.24:5000/

Submit data from the browser, then verify on `db-01`:

    ssh db-01
    sudo mysql app_db -e "SELECT * FROM users;"

Expected result:

- the HTTP response is returned without error
- the HTML form is displayed
- submitted data is inserted into the `users` table

Important:

- a running service alone is not enough
- always validate both the web response and the database write path

---

## Step 10 - Validate reboot resilience

On `app-01`:

    sudo reboot

After the VM comes back:

    ssh app-01
    systemctl status flask-user-app

Then test again:

    curl http://192.168.1.24:5000/

Expected result:

- the service starts automatically after reboot
- the application remains reachable
- no manual restart is needed

---

## Common Issues Encountered

### 1. Variables not loaded

Error example:

    'app_group' is undefined

Cause:

- variables were stored in a location Ansible did not load for the selected inventory

Solution:

- move shared variables to `inventory/dev/group_vars/all.yml`
- verify with `ansible-inventory --host app-01`

---

### 2. Incorrect application file paths

Error example:

    Could not find or access '/home/.../app/app.py'

Cause:

- the role expected `app/app.py`, but the real structure is `app/src/app.py`

Solution:

- copy `app/src/app.py`
- copy `app/src/templates/`
- keep `app/requirements.txt` as a separate file

---

### 3. Missing HTML template

Error example:

    jinja2.exceptions.TemplateNotFound: index.html

Cause:

- `index.html` was not deployed to the target host

Solution:

- ensure `app/src/templates/index.html` exists
- ensure the role copies the full templates directory into `/opt/app/templates/`

---

### 4. Database access denied

Error example:

    Access denied for user 'app_user'@'192.168.1.24'

Cause:

- mismatch between application credentials and MariaDB user configuration

Solution:

- align `db_user` and `db_password` everywhere
- keep credentials only in inventory variables and generated templates

---

## Result

At the end of sprint 3:

- the application runs as a systemd service
- the service restarts automatically after reboot or failure
- application configuration is externalized through environment variables
- deployment values are centralized in inventory variables
- the app role is cleaner and more reproducible
- the full stack is still deployable through `playbooks/site.yml`

---

## Key Takeaway

Sprint 3 is the transition from "working deployment" to "operationally safer deployment".

The main lessons are:

- one source of truth for variables is essential
- runtime management should be delegated to the operating system
- idempotent deployment is easier when paths, variables, and handlers are consistent
- validating the full request flow is more important than checking process status alone
