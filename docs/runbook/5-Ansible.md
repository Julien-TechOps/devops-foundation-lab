# 5 - Ansible Foundations

## Goal
Set up Ansible to manage the lab infrastructure and prepare reproducible deployment.

## Why
Manual deployment helped understand the stack.
Ansible is introduced to make configuration and deployment repeatable.

---

## Step 1 - Install and verify Ansible locally

Check whether Ansible is available:

    ansible --version

If not installed:

    sudo apt update
    sudo apt install ansible -y

Expected result:
- Ansible command is available
- Version is displayed without error

---

## Step 2 - Create the dev inventory

Create `inventory/dev/hosts.ini` to describe the current lab machines:

    [app]
    app-01 ansible_host=192.168.1.24 ansible_user=ubuntu

    [db]
    db-01 ansible_host=192.168.1.43 ansible_user=ubuntu

    [all:vars]
    ansible_ssh_private_key_file=~/.ssh/devops-foundation-lab
    ansible_python_interpreter=/usr/bin/python3

Why:
- Hosts are grouped by role (`app`, `db`)
- Prepares role-based deployment
- Centralizes SSH configuration

---

## Step 3 - Validate SSH connectivity with ansible ping

    ansible app -i inventory/dev/hosts.ini -m ping
    ansible db -i inventory/dev/hosts.ini -m ping

Expected result:
- Each host returns `"pong"`

If failure:
- check SSH key
- verify IP addresses
- confirm Python is installed on target hosts

---

## Step 4 - Define project structure for roles and playbooks

    playbooks/
    ├── site.yml
    ├── app.yml
    └── db.yml

    roles/
    ├── common/
    │   └── tasks/main.yml
    ├── app/
    │   └── tasks/main.yml
    └── db/
        └── tasks/main.yml

Why:
- `roles/` contains reusable configuration logic
- `playbooks/` orchestrate role execution
- Separation improves readability and scalability

---

## Step 5 - Configure roles path

Issue encountered:
Ansible could not find the `common` role.

Root cause:
Default roles path does not include project `roles/` directory.

Solution:
Create `ansible.cfg` at project root:

    [defaults]
    roles_path = ./roles


Create `playbooks/common.yml`:

    - name: Apply common configuration
      hosts: all
      become: true

      roles:
        - common

Validation:

    ansible-playbook -i inventory/dev/hosts.ini playbooks/common.yml

Expected result:
- Ansible resolves the `common` role correctly
- The playbook runs against both hosts without role resolution errors

## Step 6 - Create the common role tasks

Create `roles/common/tasks/main.yml`:

    - name: Update apt cache
      apt:
        update_cache: true
        cache_valid_time: 3600

    - name: Install base packages
      apt:
        name:
          - python3
          - python3-pip
          - net-tools
        state: present

Why:
- `python3` ensures a consistent Python environment on target hosts
- `python3-pip` prepares future Python package installation
- `net-tools` provides basic network troubleshooting tools
- `cache_valid_time` prevents unnecessary apt cache updates and improves idempotence

---

Validation:

Run the playbook:

    ansible-playbook -i inventory/dev/hosts.ini playbooks/common.yml

Run it a second time:

    ansible-playbook -i inventory/dev/hosts.ini playbooks/common.yml

Expected result:
- first run may install packages or refresh apt cache
- second run should show no unnecessary changes (`changed=0` or minimal)
- no errors on any host

---

Key takeaway:
The `common` role establishes a minimal, reusable baseline across all hosts.
Idempotence is a core principle: the same playbook can be executed multiple times without introducing unintended changes.

## Step 7 - Provision MariaDB with Ansible

Goal

Install and start MariaDB on the database host using Ansible.

Why

The database is a critical component of the application stack.
It must be:

installed automatically
started reliably
reproducible across environments

This step focuses only on system-level setup (not database configuration yet).

### Create the database playbook

Create playbooks/db.yml:

- name: Apply database configuration
  hosts: db
  become: true

  roles:
    - db

### Implement the db role

Create roles/db/tasks/main.yml:

- name: Install MariaDB server
  apt:
    name: mariadb-server
    state: present
    update_cache: true
    cache_valid_time: 3600

- name: Ensure MariaDB is started and enabled
  service:
    name: mariadb
    state: started
    enabled: true

### Run the playbook

ansible-playbook -i inventory/dev/hosts.ini playbooks/db.yml

### Validate installation

Check service status (on db-01) : 

    ssh ubuntu@192.168.1.43
    systemctl status mariadb

Expected:

    service is active (running)

Check MariaDB access

    sudo mysql

Expected:

access to MariaDB prompt without password (unix_socket auth)

### Validate idempotency

Run the playbook again:

ansible-playbook -i inventory/dev/hosts.ini playbooks/db.yml

Expected:

no errors
minimal or no changes
service remains stable

Result :

MariaDB is installed on db-01
service is running and enabled at boot
provisioning is reproducible via Ansible

## Step 8 - Configure database (DB + user)

### Goal
Automate the creation of the application database and user in MariaDB.

### Why
After installing and starting MariaDB, the database must be prepared to:
- store application data
- allow external connections from the application server

This step introduces database-level automation using Ansible MySQL modules.

---

### 1. Install required Python driver

Add to `roles/db/tasks/main.yml`:

    - name: Install PyMySQL driver
      apt:
        name: python3-pymysql
        state: present

Why:
- required by Ansible MySQL modules
- enables communication between Ansible and MariaDB

---

### 2. Create application database

    - name: Create application database
      community.mysql.mysql_db:
        name: app_db
        state: present
        login_unix_socket: /var/run/mysqld/mysqld.sock

---

### 3. Create application user

    - name: Create application user
      community.mysql.mysql_user:
        name: app_user
        password: password
        priv: "app_db.*:ALL"
        host: "%"
        state: present
        login_unix_socket: /var/run/mysqld/mysqld.sock

Why:
- user is accessible from any host (`%`)
- required for application connectivity from `app-01`

---

### 4. Run the playbook

    ansible-playbook -i inventory/dev/hosts.ini playbooks/db.yml

---

### 5. Validate database and user

On `db-01`:

    sudo mysql -e "SHOW DATABASES;"
    sudo mysql -e "SELECT User, Host FROM mysql.user;"

Expected:
- `app_db` exists
- `app_user` exists with host `%`

---

### 6. Validate idempotency

Run again:

    ansible-playbook -i inventory/dev/hosts.ini playbooks/db.yml

Expected:
- no errors
- no unnecessary changes (`changed=0`)

---

### Result

- database `app_db` is created
- user `app_user` is configured with proper privileges
- configuration is reproducible and stable

---

### Key takeaway

This step demonstrates the transition from:
- system configuration (installing MariaDB)
to:
- service configuration (managing database state)

Ansible modules ensure idempotent management of database resources.

## Step 9 - Apply database schema

### Goal
Import the initial SQL schema required by the application.

### Why
After provisioning MariaDB and creating the application database, the schema must be applied so that the application can store user data.

This step creates the `users` table used by the Flask application.

---

### 1. Prepare the schema file

Update `sql/schema.sql` to make repeated imports safer:

    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        first_name VARCHAR(50),
        last_name VARCHAR(50)
    );

Why:
- prevents failure if the table already exists
- makes repeated execution more tolerant in a lab context

---

### 2. Copy the schema file to the database host

Add to `roles/db/tasks/main.yml`:

    - name: Copy schema.sql
      copy:
        src: ../../sql/schema.sql
        dest: /tmp/schema.sql

---

### 3. Import the schema

    - name: Import schema
      community.mysql.mysql_db:
        name: app_db
        state: import
        target: /tmp/schema.sql
        login_unix_socket: /var/run/mysqld/mysqld.sock

---

### 4. Run the playbook

    ansible-playbook -i inventory/dev/hosts.ini playbooks/db.yml

---

### 5. Validate schema import

On `db-01`:

    sudo mysql app_db -e "SHOW TABLES;"
    sudo mysql app_db -e "DESCRIBE users;"

Expected:
- the `users` table exists in `app_db`
- table structure includes:
  - `id`
  - `first_name`
  - `last_name`

Observed result:

    +------------+-------------+------+-----+---------+----------------+
    | Field      | Type        | Null | Key | Default | Extra          |
    +------------+-------------+------+-----+---------+----------------+
    | id         | int(11)     | NO   | PRI | NULL    | auto_increment |
    | first_name | varchar(50) | YES  |     | NULL    |                |
    | last_name  | varchar(50) | YES  |     | NULL    |                |
    +------------+-------------+------+-----+---------+----------------+

---

### 6. Re-run and observe behavior

Run the same playbook again:

    ansible-playbook -i inventory/dev/hosts.ini playbooks/db.yml

Observed result:
- schema import task runs again
- playbook remains functional
- task reports changes (`changed=1`)

---

### Result

- schema is imported successfully
- `users` table is available for the application
- repeated execution is tolerated without failure

---

### Limitation

The schema import task is functional but not fully idempotent.

Using `community.mysql.mysql_db` with `state: import` re-executes the SQL import on each run.
This is acceptable for the current learning stage, but a more advanced project would require a better schema migration strategy. 

## Step 10 - Application installation and configuration

### Goal
Deploy the Flask application on `app-01` using an Ansible role.

### Why
The application must be deployed in a repeatable, automated, and controlled way.

---

### 1. Install Python system packages

    - name: Install Python system packages
    apt:
        name:
        - python3
        - python3-pip
        - python3-venv
        state: present
        update_cache: true
        cache_valid_time: 3600

Why:
- ensures required Python runtime is present on the target host
- uses cache_valid_time to avoid unnecessary apt updates
- guarantees consistent environment before deploying the app

### 2. Create application directory

    - name: Create app directory
    file:
        path: /opt/app
        state: directory
        mode: "0755"

Why:
- standard location for deployed application
- separates application from system directories
- ensures directory exists before copying files

### 3. Copy application source code

    - name: Copy application code
    copy:
        src: ../../app/src/
        dest: /opt/app/
        
    - name: Copy requirements.txt
    copy:
        src: ../../app/requirements.txt
        dest: /opt/app/requirements.txt

Why:
- transfers application code from control node to target host
- keeps deployment simple (no git clone yet)
- prepares environment for dependency installation

### 4. Create Python virtual environment

    - name: Create virtual environment
    command: python3 -m venv /opt/app/.venv
    args:
        creates: /opt/app/.venv/bin/activate

Why:
- isolates application dependencies from system Python
- required due to modern Python packaging constraints (PEP 668)
- creates ensures idempotency (no recreation if already exists)

### 5. Install Python dependencies

    - name: Install Python requirements in virtualenv
    pip:
        requirements: /opt/app/requirements.txt
        virtualenv: /opt/app/.venv

Why:
- installs Flask and PyMySQL inside the virtual environment
- ensures consistent dependency management
- avoids conflicts with system packages

### 6. Check application runtime state

    - name: Check if Flask app is already listening on port 5000
    shell: ss -ltn '( sport = :5000 )' | grep 5000
    register: flask_port_check
    failed_when: false
    changed_when: false

Why:
- detects if the application is already running
- avoids starting duplicate processes
- ensures idempotent behavior

### 7. Start application (if not running)

    - name: Start Flask application if not already running
    shell: nohup /opt/app/.venv/bin/python /opt/app/app.py > /tmp/app.log 2>&1 &
    when: flask_port_check.rc != 0

Why:
- starts the application only if not already running
- nohup allows background execution without SSH session dependency
- basic runtime management without a process supervisor

Result: 
- application is deployed automatically via Ansible
- dependencies are installed in an isolated environment
- application is accessible via HTTP on port 5000
- deployment is repeatable and idempotent

Limitations
- application is not managed as a service (systemd)
- no automatic restart on crash
- no restart after server reboot
- application configuration is still hardcoded

## Step 11 - Full stack orchestration (site.yml)

### 1. Define site.yml

The `site.yml` playbook acts as the global entrypoint:

    - name: Apply common configuration
    hosts: all
    become: true
    roles:
        - common

    - name: Apply database configuration
    hosts: db
    become: true
    roles:
        - db

    - name: Deploy application
    hosts: app
    become: true
    roles:
        - app

### 2. Execution order

The orchestration enforces a logical order:
common → base system configuration on all hosts
db → database installation and setup on db-01
app → application deployment on app-01

This guarantees that:
- system dependencies are available
- database is ready before application connects to it

### 3. Run full deployment

    ansible-playbook -i inventory/dev/hosts.ini playbooks/site.yml

### 4. Validation

After execution:
- database is available on db-01
- application is running on app-01
- appplication is accessible via: http://<app-ip>:5000
data submitted via the web form is stored in MariaDB

Result:
- full stack deployment is executed with a single command
- infrastructure is reproducible end-to-end
- roles are orchestrated in a controlled sequence

Limitations
- no environment separation beyond inventory (dev, test)
- no CI/CD pipeline yet
- no rollback strategy
- application runtime still not managed (no systemd)