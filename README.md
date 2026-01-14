# Remote Valve Management System

A SCADA-style web application demonstrating security vulnerabilities in OT/Industrial Control Systems and their remediation strategies.

## Project Overview

This project implements a Remote Valve Management System with intentional security vulnerabilities (CWE-434, SQL Injection) to demonstrate real-world attack vectors in SCADA environments and proper security countermeasures.

**Academic Context:** CS437 Cybersecurity Assignment - OT Security  
**Institution:** Sabancı University  
**Task:** #5 - Remote Valve Management System

## Features

### Core SCADA Functionality
- Real-time valve monitoring dashboard
- Valve open/close percentage control (0-100%)
- Command execution with timestamp tracking
- Communication status monitoring (connected/disconnected/timeout)
- Valve operation scheduling
- Force re-synchronization capability
- Comprehensive logging system:
  - Command execution logs
  - Failed valve response logs
  - Communication timeout logs

### Security Features
- Role-based access control (Admin, Operator)
- Attack monitoring and classification system
- Real-time security event logging
- Admin-only monitoring dashboard

### File Upload Capabilities
- Firmware updates (.bin files)
- Valve configuration files (.conf files)
- Encrypted file handling (AES encryption)
