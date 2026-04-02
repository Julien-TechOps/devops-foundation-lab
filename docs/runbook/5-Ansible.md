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