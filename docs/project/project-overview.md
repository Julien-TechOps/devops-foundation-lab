# Project Overview

## Purpose

This document provides a high-level view of the project from a product and delivery perspective.

It focuses on:
- scope
- priorities
- evolution of the system

Technical details are documented in the main README.

---

## Themes

- Application Functionality  
- Infrastructure & Environment  
- Automation (Ansible)  
- Reliability & Delivery  

---

## Epics

- Build a minimal functional application  
- Set up a working infrastructure  
- Automate configuration and deployment  
- Improve reliability and delivery process  

---

## Current Status

- Sprint 1 MVP manual deployment: DONE  
- Sprint 2 Ansible foundations: DONE  
- Sprint 3 production-readiness improvements: NEXT  

---

## Roadmap

### Current Focus
- Freeze Sprint 2 deliverables and documentation
- Prepare Sprint 3 around runtime reliability and configuration management

### Next
- Replace `nohup` with a `systemd` service
- Move hardcoded configuration into `group_vars/`
- Clean up application deployment logic and make it more maintainable

### Later
- Infrastructure provisioning automation
- Environment separation (dev/test)
- Health checks
- CI/CD pipeline
- Containerization
- Monitoring

---

## Principles

- Keep MVP simple and functional  
- Automate only after understanding manual steps  
- Separate infrastructure, configuration, and application  
- Iterate in small, validated steps  
