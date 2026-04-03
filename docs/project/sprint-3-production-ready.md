# Sprint 3 - Application Production Readiness

## Objective
Make the application reliable, configurable, and closer to production standards.

## Scope
- Replace `nohup` with a systemd service
- Externalize application configuration (DB connection)
- Introduce Ansible variables (`group_vars`)
- Clean application deployment logic

## Context
Sprint 2 delivered working Ansible-based deployment for the full stack.
Sprint 3 starts from that stable baseline and focuses on reliability, maintainability, and cleaner configuration management rather than adding major new functional scope.

---

## Planned Work

### 1. Application runtime (systemd)

- Create a systemd service for the Flask app
- Ensure:
  - auto-start on boot
  - restart on failure
  - proper logging

---

### 2. Configuration management

- Remove hardcoded DB config from `app.py`
- Inject configuration via:
  - environment variables OR
  - Ansible variables

---

### 3. Ansible variables

- Move hardcoded values into:
  - `group_vars/all.yml`
  - or `group_vars/dev.yml`

Examples:
- DB_HOST
- DB_USER
- DB_PASSWORD
- APP_PORT

---

### 4. Improve app role

- Ensure idempotent restart when config changes
- Remove fragile runtime logic (port check + nohup)
- Prepare service-based deployment

---

## Expected Outcome

- The stack remains deployable through `playbooks/site.yml`
- The application process becomes manageable through the operating system
- Configuration is clearer and environment-oriented
- The project is better prepared for later work on testing, environments, and CI/CD

---

## Definition of Done

- Application runs as a systemd service
- Application restarts automatically on reboot
- No hardcoded configuration in `app.py`
- All configuration managed via Ansible variables
- Deployment remains fully reproducible via `site.yml`
