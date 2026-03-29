# DevOps Foundation Lab

## Overview

This repository is a learning lab to build a simple DevOps foundation around:

- a Python web application with Flask
- a MariaDB database
- local infrastructure provisioned with Multipass
- progressive automation with Ansible

The current repository reflects an MVP/manual phase: the application source code and runbooks are present, while part of the infrastructure automation skeleton is still being prepared.

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
- runbooks for:
  - Multipass setup
  - SSH setup
  - manual deployment
  - local Python environment setup

Present but not yet filled:

- `playbooks/site.yml`
- `playbooks/app.yml`
- `playbooks/db.yml`
- `inventory/dev/hosts.ini`
- `inventory/test/hosts.ini`
- `group_vars/all.yml`
- `group_vars/dev.yml`
- `group_vars/test.yml`
- `sql/schema.sql`
- `sql/seed.sql`
- `infra/multipass.sh`
- `app/src/db.py`

Important note:

The MVP app currently uses hardcoded database connection settings in `app/src/app.py`. That is acceptable for the current learning stage, but the next iteration should move these values to variables or environment-based configuration.

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
| **Deploy** | Manual deployment (MVP) → transitioning to Ansible |
| **Operate** | Services running on `app-01` and `db-01` |
| **Monitor** | Planned (health checks, logs, observability) |

---

### 📌 Current Focus

The current phase focuses on improving the **Deploy** stage by introducing Ansible-based automation.

---

### 🔄 Approach

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

## Documentation

Technical runbooks are available in `docs/runbook/`:

- [`docs/runbook/1-multipass.md`](docs/runbook/1-multipass.md)
- [`docs/runbook/2-ssh.md`](docs/runbook/2-ssh.md)
- [`docs/runbook/3-manual-deployment.md`](docs/runbook/3-manual-deployment.md)
- [`docs/runbook/4-local-python-environment.md`](docs/runbook/4-local-python-environment.md)

Recommended reading order:

1. Multipass setup
2. SSH access setup
3. Manual deployment
4. Local Python environment

Project planning documents are available in `docs/project/`:

- [`docs/project/project-overview.md`](docs/project/project-overview.md)
- [`docs/project/backlog.md`](docs/project/backlog.md)
- [`docs/project/sprint-1-mvp.md`](docs/project/sprint-1-mvp.md)
- [`docs/project/sprint-2-ansible.md`](docs/project/sprint-2-ansible.md)

Suggested reading order:

1. Project overview
2. Backlog
3. Sprint 1 MVP
4. Sprint 2 Ansible foundations

---

## Suggested Roadmap

1. fill `sql/schema.sql` and `sql/seed.sql`
2. formalize inventories in `inventory/dev/hosts.ini` and `inventory/test/hosts.ini`
3. define shared variables in `group_vars/`
4. automate MariaDB provisioning in `playbooks/db.yml`
5. automate application deployment in `playbooks/app.yml`
6. orchestrate everything from `playbooks/site.yml`
7. replace hardcoded credentials with safer configuration
8. add validation, tests, and CI/CD steps

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
