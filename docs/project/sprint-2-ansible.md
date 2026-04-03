# Sprint 2 - Ansible Foundations

## Objective
Make deployment reproducible with Ansible across the lab infrastructure.

## Scope
- Create the `dev` inventory
- Validate SSH connectivity with `ansible ping`
- Configure Ansible roles path in `ansible.cfg`
- Implement role `common`
- Implement role `db`
- Implement role `app`
- Implement global orchestration with `playbooks/site.yml`

## Delivered
- `inventory/dev/hosts.ini` defines `app-01` and `db-01`
- `ansible.cfg` points Ansible to the local `roles/` directory
- `playbooks/common.yml` applies the `common` role on all hosts
- `roles/common/tasks/main.yml` updates APT cache and installs base packages
- `playbooks/db.yml` applies the `db` role on database hosts
- `roles/db/tasks/main.yml` installs MariaDB, enables the service, installs `python3-pymysql`, creates `app_db`, creates `app_user`, and imports `sql/schema.sql`
- `playbooks/app.yml` applies the `app` role on application hosts
- `roles/app/tasks/main.yml` installs Python packages, copies the Flask app, creates a virtualenv, installs Python dependencies, and starts the application on port `5000`
- `playbooks/site.yml` orchestrates `common`, `db`, and `app` from a single entrypoint

## End-of-Sprint Status
- Sprint goal achieved: deployment is reproducible with Ansible on the `dev` environment
- Main limitation kept at the end of Sprint 2: the application runtime is still managed with `nohup`
- Configuration is still partially hardcoded in both the application and Ansible tasks
- The automation is functional, but not yet production-oriented

## Remaining Work For Sprint 3
- Move database connection settings and credentials out of `app/src/app.py`
- Replace hardcoded values in Ansible tasks with variables from `group_vars/`
- Add Ansible Galaxy dependencies if `community.mysql` must be installed explicitly via `requirements.yml`
- Improve application process management with a proper service instead of `nohup`

## Definition of Done
- `ansible ping` works on the `dev` inventory
- MariaDB provisioning is automated
- Application deployment is automated
- Playbook execution is repeatable
- Full stack orchestration is available from `playbooks/site.yml`

## Retrospective

### What went well
- The project moved from manual deployment to repeatable Ansible-based deployment
- Roles are clearly separated between common system setup, database provisioning, and application deployment
- `site.yml` now provides a single entrypoint for the deployment sequence

### What can be improved
- Runtime management is fragile because the Flask process is started with `nohup`
- Configuration is duplicated and hardcoded in multiple places
- Variables and collection dependencies are not yet formalized

### Next focus
- Make the application deployment more production-ready in Sprint 3
