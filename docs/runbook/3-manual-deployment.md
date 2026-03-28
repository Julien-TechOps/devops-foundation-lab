# Manual Deployment Runbook — DevOps Foundation Lab

## Objective

This runbook explains how to manually deploy the MVP of the project:

- a Python web application running on `app-01`
- a MariaDB database running on `db-01`
- a simple web form to store `first_name` and `last_name` in the database

This document is written as a learning guide, not only as a command list.

---

## Target Architecture

- `app-01`: application server
- `db-01`: database server

Application flow:

1. user opens the web form in a browser
2. user submits first name and last name
3. Flask application receives the form
4. Python connects to MariaDB on `db-01`
5. data is inserted into the `users` table

---

## Prerequisites

Before starting, the following must already exist:

(see ./docs/runbook/3-multipass.md)

- Multipass installed on Windows
- two running VMs:
  - `app-01`
  - `db-01`
- VM IP addresses identified on the `192.168.x.x` network

(see docs/runbook/2-ssh.md)

- SSH access working from WSL to both VMs

Example used in this runbook:

- `app-01` → `192.168.1.24`
- `db-01` → `192.168.1.43`

---

## Step 1 — Connect to the database VM

bash :

    ssh db-01

Why : We first prepare the database server because the application depends on it.

## Step 2 — Install MariaDB on db-01

    sudo apt update
    sudo apt install mariadb-server -y

Why : MariaDB is the database engine that will store user data.

## Step 3 — Start and enable MariaDB

    sudo systemctl start mariadb
    sudo systemctl enable mariadb

Why : 
    - start launches the database service now
    - enable ensures the service starts automatically after reboot

## Step 4 — Allow remote database connections

Open the MariaDB server configuration:

    sudo nano /etc/mysql/mariadb.conf.d/50-server.cnf

Find this line:

    bind-address = 127.0.0.1 

and replace it with :  

    bind-address = 0.0.0.0

Restart MariaDB: 

    sudo systemctl restart mariadb

Why :
By default, MariaDB listens only on localhost (127.0.0.1), which means only the local machine can connect.
Our application runs on another VM (app-01), so MariaDB must listen on all interfaces.

## Step 5 — Create the database, user and table

Open MariaDB:

    sudo mysql

Run:

    CREATE DATABASE app_db;
    CREATE USER 'app_user'@'%' IDENTIFIED BY 'password';
    GRANT ALL PRIVILEGES ON app_db.* TO 'app_user'@'%';
    FLUSH PRIVILEGES;

    USE app_db;

    CREATE TABLE users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        first_name VARCHAR(50),
        last_name VARCHAR(50)
    );
    EXIT;

Why :
app_db is the database used by the Python app
app_user is a dedicated database user for the application
'%' means the user can connect remotely
users is the table where submitted form data is stored

## Step 6 — Verify the database server IP

    hostname -I

Important : 

Ignore the 10.0.2.15 address if present.
Use the 192.168.x.x address because it is the reachable network between VMs.
Example: db-01 → 192.168.1.43

## Step 7 — Connect to the application VM

Open another terminal:

    app-01

## Step 8 — Install Python and required packages

    sudo apt update
    sudo apt install python3 python3-pip python3-venv netcat-openbsd -y

Why : 
python3 runs the application
python3-pip installs Python libraries
python3-venv creates an isolated Python environment
netcat-openbsd provides nc, useful to test if a remote port is open

## Step 9 — Create the application workspace

    mkdir -p ~/app
    cd ~/app
    python3 -m venv .venv
    source .venv/bin/activate
    pip install flask pymysql

Why :
~/app stores the application files
.venv isolates project dependencies
flask is the web framework
pymysql allows Python to connect to MariaDB

## Step 10 — Test network connectivity to the database

    ping -c 2 192.168.1.43
    nc -zv 192.168.1.43 3306

Why :

These two commands validate two different things:

    ping -c 2 192.168.1.43
    Checks that app-01 can reach db-01 on the network.

    nc -zv 192.168.1.43 3306
    Checks that port 3306 is open on db-01 with :
        nc = netcat
        -z = scan mode, without sending data
        -v = verbose output

If this command succeeds, it means MariaDB is listening and reachable.

## Step 11 — Create the Flask application

    nano ~/app/app.py

Paste : 

from flask import Flask, request
import pymysql

app = Flask(__name__)

DB_HOST = "192.168.1.43"
DB_USER = "app_user"
DB_PASSWORD = "password"
DB_NAME = "app_db"

@app.route("/", methods=["GET"])
def form():
    return """
        <h2>DevOps Foundation Lab</h2>
        <form method="POST" action="/submit">
            First name: <input name="first_name"><br><br>
            Last name: <input name="last_name"><br><br>
            <input type="submit" value="Send">
        </form>
    """

@app.route("/submit", methods=["POST"])
def submit():
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
This is the MVP application:

    display a form
    receive submitted data
    connect to MariaDB
    insert one row into the database
    Important
    app.run(host="0.0.0.0", port=5000)

This makes Flask listen on all network interfaces.

If Flask listens only on 127.0.0.1, the browser on the host machine will not be able to access it.

## Step 12 — Start the Flask application

    cd ~/app
    source .venv/bin/activate
    python3 app.py

Expected result : Flask starts and listens on port 5000.

## Step 13 — Verify local application access

On app-01, in another terminal:

    curl http://localhost:5000
    ss -lntp | grep 5000

Why :

    curl http://localhost:5000
    Checks whether the web page is returned locally.

    ss -lntp | grep 5000
    Checks whether Python is listening on port 5000.

## Step 14 — Open the application from the browser

Open in Windows:

    http://192.168.1.24:5000

Why
This validates that the app is reachable not only locally on the VM, but from outside the VM as well.

## Step 15 — Submit a test user

Example:

    first name: Marcus
    last name: Miller

Expected result in browser:

User added!

## Step 16 — Verify inserted data in MariaDB

On db-01:

    sudo mysql -e "USE app_db; SELECT * FROM users;"

Expected result : A row appears in the users table.

# Validation Checklist : 

    - db-01 reachable from app-01
    - MariaDB port 3306 reachable
    - Flask app starts correctly
    - browser can access http://IP_APP:5000
    - form submission works
    - inserted row visible in MariaDB

# Key Learning Points

Why test ping before the app?
Because if the VMs cannot communicate, the application will never reach the database.

Why test nc -zv?
Because network reachability is not enough: the database service must also be listening on the expected port.

Why use Flask?
Flask is a lightweight Python web framework, ideal for a small MVP.

Why use a virtual environment?
It isolates project dependencies from the rest of the system.

Why use a dedicated DB user?
Applications should not connect with a root database account.

# Limits of this manual MVP

This version is intentionally simple.

Not done yet:

    no automation with Ansible
    no service persistence for Flask
    no environment variables
    no hardening
    no reverse proxy
    no CI/CD

This is normal: the goal of this .md is to validate the functional flow manually.