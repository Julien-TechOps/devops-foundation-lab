# DevOps Foundation Lab

## Overview

This repository is a learning lab to build a simple DevOps foundation around:

- a Python web application with Flask
- a MariaDB database
- local infrastructure provisioned with Multipass
- progressive automation with Ansible

The repository now reflects the end of Sprint 2: the MVP application is deployed through a first complete Ansible automation layer, and Sprint 3 is focused on making that deployment more production-ready.

---

## Objectives

- understand a two-VM application architecture
- practice reproducible setup from local workstation to target hosts
- move from manual deployment to infrastructure as code
- prepare the project for future CI/CD work

---

## Current Architecture

Host environment:

- Windows as host OS
- WSL Ubuntu for DevOps tooling
- Multipass for Ubuntu VM provisioning

Target infrastructure:

- `app-01`: Flask application server
- `db-01`: MariaDB server

Application flow:

1. A user opens the web form exposed by the Flask app.
2. The form sends `first_name` and `last_name`.
3. The application connects to MariaDB on `db-01`.
4. Data is inserted into the `users` table.

---

## Repository Structure

- `app/`  
  Application codebase, Python dependencies, and test area

- `app/src/app.py`  
  Current Flask MVP entrypoint

- `app/src/db.py`  
  Database connection logic and future abstraction layer

- `playbooks/`  
  Ansible playbooks used to configure and deploy the stack

- `inventory/`  
  Environment-specific Ansible inventories (`dev`, `test`)

- `group_vars/`  
  Shared and environment-specific Ansible variables

- `sql/`  
  Database schema definition and seed data

- `infra/`  
  Infrastructure provisioning scripts used to create virtual machines

- `docs/runbook/`  
  Step-by-step operational and learning documentation

- `docs/project/`  
  Project tracking, sprint scope, roadmap, and backlog

---

## Current State

Implemented:

- Flask MVP in [`app/src/app.py`](app/src/app.py)
- Python dependencies in [`app/requirements.txt`](app/requirements.txt)
- Ansible inventory for `dev` in [`inventory/dev/hosts.ini`](inventory/dev/hosts.ini)
- Ansible configuration in [`ansible.cfg`](ansible.cfg)
- reusable `common` role in [`roles/common/tasks/main.yml`](roles/common/tasks/main.yml)
- database deployment role in [`roles/db/tasks/main.yml`](roles/db/tasks/main.yml)
- application deployment role in [`roles/app/tasks/main.yml`](roles/app/tasks/main.yml)
- playbooks:
  - [`playbooks/common.yml`](playbooks/common.yml)
  - [`playbooks/db.yml`](playbooks/db.yml)
  - [`playbooks/app.yml`](playbooks/app.yml)
  - [`playbooks/site.yml`](playbooks/site.yml)
- SQL schema in [`sql/schema.sql`](sql/schema.sql)
- runbooks for:
  - Multipass setup
  - SSH setup
  - manual deployment
  - local Python environment setup
  - Ansible foundations

Still incomplete or intentionally minimal:

- [`group_vars/all.yml`](group_vars/all.yml), [`group_vars/dev.yml`](group_vars/dev.yml), and [`group_vars/test.yml`](group_vars/test.yml) are empty
- [`requirements.yml`](requirements.yml) is empty
- [`sql/seed.sql`](sql/seed.sql) is empty
- [`inventory/test/hosts.ini`](inventory/test/hosts.ini) is not yet documented here as an active environment
- [`app/src/db.py`](app/src/db.py) is present but not used by the Flask entrypoint

Important note:

The Flask app currently uses hardcoded database connection settings in [`app/src/app.py`](app/src/app.py), and the Ansible `db` role also contains hardcoded database credentials. This is acceptable for the current learning stage, but the next iteration should move these values to `group_vars/` or environment-based configuration.

Sprint status:

- Sprint 1: MVP manual deployment completed
- Sprint 2: Ansible foundations completed
- Sprint 3: production-readiness improvements planned

---

## DevOps Lifecycle

This project follows a simplified DevOps lifecycle, progressively implemented through each phase of the lab.

| Stage   | Implementation in this project |
|--------|-------------------------------|
| **Plan** | Backlog and sprint structure in `docs/project/` |
| **Code** | Flask application and infrastructure code |
| **Build** | Python dependencies via `requirements.txt` (future: containerization) |
| **Test** | Manual validation of application and database interactions |
| **Release** | Versioning with Git and GitHub |
| **Deploy** | Manual deployment (Sprint 1) and Ansible-based deployment (Sprint 2) |
| **Operate** | Services running on `app-01` and `db-01` |
| **Monitor** | Planned (health checks, logs, observability) |

---

## Current Focus

The current phase is the transition between Sprint 2 and Sprint 3: the deployment is automated, and the next focus is runtime reliability, cleaner configuration, and better Ansible maintainability.

---

## Approach

This project is built iteratively:

- start with a working MVP  
- understand each step manually  
- progressively automate and improve reliability  

The objective is to move from a **manual deployment** to a **fully automated and reproducible system**.

## Application

The current application is a minimal Flask form that:

- serves a simple HTML form on `/`
- accepts a POST on `/submit`
- inserts submitted values into MariaDB using `pymysql`

Python dependencies:

- `flask`
- `pymysql`

Install them locally from the `app/` directory:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run locally from `app/src/`:

```bash
python3 app.py
```

By default, the app listens on:

- `0.0.0.0:5000`

---

## Ansible Deployment

Current Ansible coverage:

- `common` installs baseline packages on all hosts
- `db` installs and starts MariaDB, creates `app_db`, creates `app_user`, and imports the schema
- `app` installs Python runtime packages, copies the Flask source, creates a virtual environment, installs dependencies, and starts the app
- `site.yml` orchestrates the full deployment sequence across all target hosts

Main commands:

```bash
ansible all -i inventory/dev/hosts.ini -m ping
ansible-playbook -i inventory/dev/hosts.ini playbooks/common.yml
ansible-playbook -i inventory/dev/hosts.ini playbooks/db.yml
ansible-playbook -i inventory/dev/hosts.ini playbooks/app.yml
ansible-playbook -i inventory/dev/hosts.ini playbooks/site.yml
```

Current limitations:

- the Flask process is started with `nohup`, not a systemd service
- some values are still hardcoded instead of managed through variables
- `group_vars/` and `requirements.yml` are still not used as first-class configuration sources

---

## Documentation

Technical runbooks are available in `docs/runbook/`:

- [`docs/runbook/1-multipass.md`](docs/runbook/1-multipass.md)
- [`docs/runbook/2-ssh.md`](docs/runbook/2-ssh.md)
- [`docs/runbook/3-manual-deployment.md`](docs/runbook/3-manual-deployment.md)
- [`docs/runbook/4-local-python-environment.md`](docs/runbook/4-local-python-environment.md)
- [`docs/runbook/5-Ansible.md`](docs/runbook/5-Ansible.md)

Recommended reading order:

1. Multipass setup
2. SSH access setup
3. Manual deployment
4. Local Python environment
5. Ansible foundations

Project planning documents are available in `docs/project/`:

- [`docs/project/project-overview.md`](docs/project/project-overview.md)
- [`docs/project/backlog.md`](docs/project/backlog.md)
- [`docs/project/sprint-1-mvp.md`](docs/project/sprint-1-mvp.md)
- [`docs/project/sprint-2-ansible.md`](docs/project/sprint-2-ansible.md)
- [`docs/project/sprint-3-production-ready.md`](docs/project/sprint-3-production-ready.md)

Suggested reading order:

1. Project overview
2. Backlog
3. Sprint 1 MVP
4. Sprint 2 Ansible foundations
5. Sprint 3 Production Readiness

---

## Suggested Roadmap

1. replace `nohup` with a proper `systemd` service for the Flask app
2. move database host, user, and password into `group_vars/`
3. remove hardcoded configuration from the application code and Ansible tasks
4. populate `requirements.yml` if external Ansible collections are required explicitly
5. add seed data in `sql/seed.sql` if needed for testing
6. add validation, tests, and CI/CD steps

---

## Philosophy

This lab focuses on:

- clarity over cleverness
- reproducibility
- progressive complexity
- learning by building and documenting

The goal is not only to make the stack work, but to make each step understandable and repeatable.

---

## AI-assisted development

This project was developed with the support of AI tools (ChatGPT & Codex) used as engineering assistants.

They were leveraged to:
- challenge design decisions
- accelerate problem-solving
- support code writing and refactoring
- improve documentation and structure

All technical choices, architecture decisions, and validations remain fully understood and owned.

The goal is not to replace engineering thinking, but to enhance it through iteration, feedback, and critical reasoning.
