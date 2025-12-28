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

## Project Structure

```
task_5_CS437/
├── README.md                    # This file
├── ARCHITECTURE.md              # Detailed system design
├── todo.md                      # Development progress tracker
├── vulnerable/                  # Vulnerable version (CWE-434 + SQLi)
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── app/
│   │   ├── app.py              # Main Flask application
│   │   ├── models.py           # Database models
│   │   ├── routes/             # Route handlers
│   │   │   ├── auth.py
│   │   │   ├── dashboard.py
│   │   │   ├── valves.py
│   │   │   ├── upload.py       # 3 vulnerable upload scenarios
│   │   │   ├── monitoring.py
│   │   │   └── logs.py
│   │   ├── templates/          # HTML templates
│   │   ├── static/             # CSS, JS, images
│   │   └── utils/              # Helper functions
│   ├── init_db.py              # Database schema creation
│   └── populate_db.py          # Generate 100+ valve records
├── patched/                     # Secure version (all vulnerabilities fixed)
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── app/
│   │   └── [same structure as vulnerable]
│   ├── init_db.py
│   └── populate_db.py
└── docker-compose.yml           # Run both versions simultaneously
```

## Two Versions

### 🔴 Vulnerable Version (Port 5000)
Contains intentional security flaws for educational demonstration:

1. **CWE-434 Scenario 1:** Unrestricted file upload (no validation)
2. **CWE-434 Scenario 2:** Weak protections (bypassable size limit + blacklist)
3. **CWE-434 Scenario 3:** Encrypted file scan bypass
4. **SQL Injection:** Role-based conditional escaping (admin vulnerable, operator safe)

### 🟢 Patched Version (Port 5001)
Implements proper security controls:
- Allow-list file validation with magic byte checking
- Parameterized SQL queries (role-independent)
- Decrypt-then-scan file handling
- Input sanitization and validation
- CSRF protection
- Secure session management

## Quick Start

### Prerequisites
- Docker (version 20.10+)
- Docker Compose (version 2.0+)

### Installation & Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd task_5_CS437
```

2. Build and start both applications:
```bash
docker-compose up --build
```

3. Access the applications:
   - **Vulnerable Version:** http://localhost:5000
   - **Patched Version:** http://localhost:5001

### Default Credentials

| Username | Password | Role |
|----------|----------|------|
| admin | admin123 | Administrator |
| operator | operator123 | Operator |

## Vulnerabilities Demonstrated

### 1. CWE-434: Unrestricted Upload of File with Dangerous Type

#### Scenario 1: No Protection
- **Endpoint:** `/upload/scenario1`
- **Access:** Admin only
- **Vulnerability:** Zero validation, any file type/size accepted
- **Exploitation:** Upload web shell, achieve RCE

#### Scenario 2: Insufficient Protection
- **Endpoint:** `/upload/scenario2`
- **Access:** Admin only
- **Vulnerabilities:**
  - File size limit (bypassable via header manipulation)
  - Extension blacklist (incomplete, allows .php5, .phtml, double extensions)
- **Exploitation:** Bypass filters using alternate extensions or MIME spoofing

#### Scenario 3: Encrypted File Bypass
- **Endpoint:** `/upload/scenario3`
- **Access:** Admin only
- **Vulnerability:** Malware scan only checks plaintext; encrypted files bypass scanning
- **Exploitation:** Upload AES-encrypted malicious payload, decrypt post-upload

### 2. SQL Injection: Conditional Escaping Based on User Role

- **Endpoint:** `/valves/search`
- **Access:** Authenticated (both roles)
- **Vulnerability:** Admin queries use raw SQL string concatenation; Operator queries use parameterized queries
- **Exploitation:** Admin can inject: `V-001' UNION SELECT * FROM users--`
- **Detection Challenge:** Low-privilege testing misses this vulnerability

## Testing Vulnerabilities

### Tools Required
- Burp Suite (request interception and manipulation)
- sqlmap (automated SQL injection testing)
- curl or Postman (API testing)

### Example Exploitation

#### File Upload Attack (Scenario 1)
```bash
curl -X POST http://localhost:5000/upload/scenario1 \
  -H "Cookie: session=<admin-session>" \
  -F "file=@webshell.php"
```

#### SQL Injection (Admin Role)
```bash
curl -X POST http://localhost:5000/valves/search \
  -H "Cookie: session=<admin-session>" \
  -d "search=V-001' UNION SELECT username,password_hash,role,email,1,2 FROM users--"
```

#### Size Limit Bypass (Scenario 2)
Use Burp Suite to tamper with Content-Length header while uploading oversized file.

## Monitoring System

Access the monitoring dashboard as admin:
- **URL:** http://localhost:5000/monitoring
- **Features:**
  - Real-time attack detection
  - Attack classification (SQL injection, file upload abuse, size bypass, etc.)
  - Severity levels (low, medium, high, critical)
  - Request details (IP, payload, timestamp)
  - Attack statistics and visualization

## Database Schema

### Core Tables
- **users:** Authentication and role management
- **valves:** 100+ valve records with status tracking
- **command_logs:** All valve operations logged
- **schedules:** Scheduled valve operations
- **file_uploads:** Upload tracking and metadata
- **attack_logs:** Security event monitoring

See `ARCHITECTURE.md` for complete schema details.

## Technology Stack

| Component | Technology |
|-----------|-----------|
| Backend | Flask 3.0 (Python 3.9) |
| Database | SQLite3 |
| Frontend | HTML5 + Bootstrap 5 |
| Session Management | Flask-Session |
| Encryption | PyCryptodome (AES-256) |
| File Type Detection | python-magic |
| Containerization | Docker + docker-compose |

## Development Progress

Track implementation progress in `todo.md`:
- ✅ Phase 0: Architecture & Design
- ⏳ Phase 1: Secure Baseline Application
- ⏳ Phase 2-8: Implementation, Testing, Documentation

## Assignment Requirements Checklist

- [ ] Vulnerable version with all required vulnerabilities
- [ ] Patched version with proper security controls
- [ ] 100+ valve records in database
- [ ] Population script included
- [ ] Monitoring system functional in both versions
- [ ] Each vulnerability on separate page/endpoint
- [ ] Dockerized versions (both)
- [ ] Comprehensive report
- [ ] Demonstration video
- [ ] Pentesting with Burp Suite, sqlmap, etc.

## Security Disclaimer

⚠️ **WARNING:** This application contains intentional security vulnerabilities for educational purposes only.

**DO NOT:**
- Deploy this application on public networks
- Use vulnerable version patterns in production code
- Use default credentials in real systems
- Expose vulnerable endpoints to the internet

This project is designed exclusively for controlled academic environments to teach secure coding practices.

## Team Information

**Task:** #5 - Remote Valve Management System  
**Team Size:** 3 members  
**Institution:** Sabancı University  
**Course:** CS437 - Cybersecurity

## License

This project is created for academic purposes as part of CS437 coursework.

## Support & Documentation

- **Architecture Details:** See `ARCHITECTURE.md`
- **Development Roadmap:** See `todo.md`
- **Assignment Brief:** See `task.md`

## Demonstration Session

All team members must be present for the Zoom demonstration session covering:
1. Application walkthrough (both versions)
2. Vulnerability exploitation demonstrations
3. Patch explanations and code review
4. Pentesting tool usage (Burp Suite, sqlmap)
5. Monitoring system showcase

---

**Last Updated:** December 28, 2025  
**Status:** Phase 0 Complete - Architecture Defined  
**Next Milestone:** Implement secure baseline application

