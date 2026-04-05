# Multipass Setup — DevOps Foundation Lab

## Objective

Install Multipass on Windows and create two Ubuntu virtual machines:

- app-01
- db-01

---

## Architecture Overview

Host machine:

- Windows 11
- Hyper-V (required)

VMs:

- app-01 → application server
- db-01 → database server

Both VMs are connected to the local network (Wi-Fi).

---

## Step 1 — Install Multipass

### Download

https://multipass.run/download/windows

### Installation

- Run the installer
- Select:


Add Multipass to the current user's PATH (Recommended)


- Complete installation

---

## Step 2 — Verify Installation

Open PowerShell:

multipass version

Expected result:

* Multipass version displayed

---

## Step 3 — Check Available Networks

```powershell
multipass networks
```

Example output:

```
Name       Type
Ethernet   ethernet
Wi-Fi      wifi
```

---

## Step 4 — Create Virtual Machines

### Create app-01

```powershell
multipass launch --name app-01 --network name="Wi-Fi"
```

---

### Create db-01

```powershell
multipass launch --name db-01 --network name="Wi-Fi"
```

---

## Step 5 — Verify VMs

```powershell
multipass list
```

Expected output:

```
Name     State    IPv4
app-01   Running  192.168.x.x
db-01    Running  192.168.x.x
```

Each VM must have a unique IP address.

---

## Step 6 — Access VM

```powershell
multipass shell app-01
```

Exit VM:

```bash
exit
```

---

## Notes

* Using `Wi-Fi` network allows VMs to be reachable from WSL
* Default switch (Hyper-V) may not expose usable IPs
* Each VM gets an IP from the local network (DHCP)

---

# Common Issues

## No IP address (N/A)

Cause:

* Default NAT network used

Solution:

* Recreate VM using:

```powershell
multipass launch --name <vm-name> --network name="Wi-Fi"
```

---

### Same IP for multiple VMs

Cause:

* Misconfigured or NAT network

Solution:

* Delete and recreate VMs on Wi-Fi network

---

### Invalid network options supplied

Cause:

* Wrong network name syntax

Wrong:

```powershell
--network "Default Switch"
```

Correct:

```powershell
--network name="Wi-Fi"
```

---

## Cleanup Commands

Delete VMs:

```powershell
multipass delete app-01 db-01
```

Purge:

```powershell
multipass purge
```

---

## Result

Two Ubuntu VMs created, accessible from WSL and ready for SSH and Ansible provisioning.

# VM Lifecycle Management
## List VMs
multipass list

## Stop a VM
multipass stop app-01

## Stop all VMs:
multipass stop --all

## Start a VM
multipass start app-01

## Start all VMs:
multipass start --all

## Restart a VM
multipass restart app-01

## Delete a VM
multipass delete app-01
multipass purge

## Check VM status
multipass list
Possible states:
Running
Stopped
Deleted