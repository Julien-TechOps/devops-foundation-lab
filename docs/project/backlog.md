# Product Backlog

## DONE (Sprint 1)
- MVP Flask app
- MariaDB setup
- VM provisioning (manual)
- SSH access
- Documentation (runbook)

## DONE (Sprint 2)
- Ansible inventory setup
- Ansible connectivity (ping)
- Role: common
- Role: db
- Role: app
- site.yml orchestration

## NEXT (Sprint 3)
- Application runtime (systemd)
- Externalize application configuration
- Move hardcoded values to `group_vars/`
- Improve app role idempotency and service management

## LATER
- Automate VM provisioning (Multipass script)
- Health checks
- Environment separation (dev/test)
- CI/CD pipeline
- Dockerization
- Monitoring
