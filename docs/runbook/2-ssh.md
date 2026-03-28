# SSH Access Setup — DevOps Foundation Lab

## Objective

Establish secure and reproducible SSH access from WSL (Ubuntu) to Multipass virtual machines.

---

## Architecture

- Host: Windows 11
- Dev environment: WSL (Ubuntu)
- VM provider: Multipass
- Target VMs:
  - app-01 (192.168.1.24)
  - db-01 (192.168.1.43)

---

## Step 1 - Generate SSH Key

WSL/ linux :
ssh-keygen -t ed25519 -f ~/.ssh/devops-foundation-lab -C "devops-foundation-lab"

## Step 2 - Add Public Key to VM

Connect to VM : 
multipass shell app-01

Prepare SSH directory
mkdir -p ~/.ssh
chmod 700 ~/.ssh

Add public key
nano ~/.ssh/authorized_keys

Paste the content of:
cat ~/.ssh/devops-foundation-lab.pub

Then apply permissions:
chmod 600 ~/.ssh/authorized_keys

Repeat the same process for db-01.

## Step 3 — Configure SSH Client

Edit SSH config:

nano ~/.ssh/config

Host app-01
    HostName 192.168.1.24
    User ubuntu
    IdentityFile ~/.ssh/devops-foundation-lab

Host db-01
    HostName 192.168.1.43
    User ubuntu
    IdentityFile ~/.ssh/devops-foundation-lab
    
## Step 4 — Test Connection

ssh app-01
ssh db-01

Expected result:
- No password prompt
- Direct access to VM

SSH Access Flow

WSL (SSH client)
   ↓
Private key (~/.ssh/devops-foundation-lab)
   ↓
VM (~/.ssh/authorized_keys)
Result

Passwordless and reproducible SSH access to all lab VMs.