# Remote Valve Management System - Development Tracker

## Project Overview
Building a SCADA-style web interface with intentional vulnerabilities for cybersecurity demonstration.
Two versions: Vulnerable (with CWE-434 + SQL injection) and Patched (secure implementation).

---

## PHASE 0: Architecture & Constraints ✅
**Status:** COMPLETED  
**Goal:** Design system architecture before writing any code

### Tasks:
- [x] Define technology stack (Flask, database choice, frontend)
- [x] Design database schema (valves, logs, users, uploads)
- [x] Define user roles and permissions (admin, operator)
- [x] Map REST API endpoints
- [x] Design file upload workflow (safe baseline)
- [x] Define logging strategy and events to track
- [x] Document monitoring dashboard requirements

**Deliverables:**
- ✅ Architecture document (ARCHITECTURE.md)
- ✅ Database schema with 6 tables
- ✅ API endpoint list (23 endpoints)
- ✅ User role definitions (admin vs operator)

---

## PHASE 1: Safe Baseline Application ✅
**Status:** COMPLETED  
**Goal:** Build fully functional, SECURE SCADA interface (becomes patched version later)

### Core Features:
- [x] User authentication system (login/logout)
- [x] Role-based access control (admin vs operator)
- [x] Valve dashboard (view status, open/close %, timestamp, comm status)
- [x] Valve control (open/close operations)
- [x] Valve scheduling system
- [x] Force re-synchronization feature
- [x] Command execution logs
- [x] Failed valve response logs
- [x] Communication timeout logs
- [x] Safe file upload (config/firmware with proper validation)
- [x] Database population script (150 valve records)

**Technical Requirements:**
- [x] Flask application structure
- [x] Database setup and models
- [x] HTML templates (industrial SCADA-style UI with Bootstrap)
- [x] Secure input validation
- [x] Parameterized SQL queries
- [x] Proper file upload validation
- [x] Session management

**Deliverables:**
- ✅ Working Flask application (patched/ directory)
- ✅ Database with 150 valve records
- ✅ Population script functional
- ✅ Clean, documented code

---

## PHASE 2: Clone to Vulnerable Version ⏳
**Status:** Not Started  
**Goal:** Create separate codebase for vulnerable implementation

### Tasks:
- [ ] Copy baseline application to separate directory
- [ ] Set up separate folder structure (vulnerable/ and patched/)
- [ ] Ensure both versions run independently
- [ ] Document version differences in README

**Deliverables:**
- Two separate application directories
- Both versions functional at this point

---

## PHASE 3: Implement Vulnerabilities ⏳
**Status:** Not Started  
**Goal:** Intentionally introduce security flaws in vulnerable version

### A) CWE-434 File Upload Vulnerabilities (3 separate pages/endpoints):

#### Vulnerability 1: No Protection
- [ ] Create upload endpoint with ZERO validation
- [ ] Allow any file type, any size
- [ ] Store files in web-accessible directory
- [ ] Test: Upload PHP/Python reverse shell

#### Vulnerability 2: Insufficient Protection (2 weak mechanisms)
- [ ] Implement file size limit (bypassable)
- [ ] Implement blacklist/MIME check (bypassable)
- [ ] Document how both can be bypassed
- [ ] Test: Bypass using double extensions, MIME manipulation

#### Vulnerability 3: Encrypted File Bypass
- [ ] Implement plaintext-only malware scanner
- [ ] Create encryption/decryption mechanism
- [ ] Allow upload of encrypted files (no scan)
- [ ] Decrypt files after upload (post-scan)
- [ ] Test: Upload encrypted malicious payload

### B) SQL Injection (Role-Based Conditional Escaping):
- [ ] Create search/filter input field (same for all users)
- [ ] Implement role check: if admin → raw SQL, if user → escaped
- [ ] Add comments explaining the vulnerability
- [ ] Test: SQLi works with admin credentials only
- [ ] Test: SQLi fails with user credentials

**Deliverables:**
- 4 distinct vulnerability demonstrations
- Commented code explaining WHY vulnerable
- Test cases for each vulnerability

---

## PHASE 4: Monitoring System ⏳
**Status:** Not Started  
**Goal:** Build attack detection and logging system

### Tasks:
- [ ] Create middleware for request logging
- [ ] Implement attack detection patterns:
  - [ ] File upload abuse detection
  - [ ] SQL injection pattern detection
  - [ ] Suspicious file size manipulation
  - [ ] Encrypted payload detection
- [ ] Build monitoring dashboard page
- [ ] Display attack details (timestamp, IP, payload, classification)
- [ ] Attack classification system
- [ ] Real-time or near-real-time logging
- [ ] Store attack logs in database

**Deliverables:**
- Monitoring dashboard (accessible in both versions)
- Attack classification engine
- Detailed attack logs

---

## PHASE 5: Patched Version ⏳
**Status:** Not Started  
**Goal:** Fix all vulnerabilities in patched version

### Security Fixes:

#### File Upload Patches:
- [ ] Implement allow-list for file types
- [ ] Proper file size validation
- [ ] Content-type verification (both header and magic bytes)
- [ ] Scan files AFTER decryption
- [ ] Store files outside web root
- [ ] Randomize filenames
- [ ] Add rate limiting

#### SQL Injection Patches:
- [ ] Replace ALL raw SQL with parameterized queries
- [ ] Role-independent input validation
- [ ] Use ORM for database operations
- [ ] Input sanitization

#### Additional Hardening:
- [ ] CSRF protection
- [ ] Secure session management
- [ ] Rate limiting
- [ ] Input validation everywhere
- [ ] Error handling (no info disclosure)

**Deliverables:**
- Fully patched application
- Comments explaining security fixes
- Verification that exploits no longer work

---

## PHASE 6: Dockerization ⏳
**Status:** Not Started  
**Goal:** Containerize both versions for easy deployment

### Tasks:
- [ ] Create Dockerfile for vulnerable version
- [ ] Create Dockerfile for patched version
- [ ] Create docker-compose.yml (both versions)
- [ ] Database initialization in containers
- [ ] Run population script in Docker
- [ ] Expose correct ports
- [ ] Create .dockerignore
- [ ] Test: Both versions run from scratch with docker-compose up

**Deliverables:**
- 2 Dockerfiles
- docker-compose.yml
- Build and run instructions

---

## PHASE 7: Testing & Demonstration ⏳
**Status:** Not Started  
**Goal:** Prove vulnerabilities exist and patches work

### Pentesting Tools to Use:
- [ ] **Burp Suite:** Intercept and modify requests
- [ ] **sqlmap:** Automated SQL injection testing
- [ ] **OWASP ZAP:** Vulnerability scanning
- [ ] **curl/Postman:** Manual API testing
- [ ] Custom scripts for exploitation

### Test Cases:

#### Vulnerable Version Tests:
- [ ] CWE-434 #1: Upload web shell, execute commands
- [ ] CWE-434 #2: Bypass size limit and MIME check
- [ ] CWE-434 #3: Upload encrypted malicious file
- [ ] SQL Injection: Extract database as admin
- [ ] Verify monitoring logs capture attacks

#### Patched Version Tests:
- [ ] All upload bypasses fail
- [ ] SQL injection attempts blocked
- [ ] Verify error handling doesn't leak info
- [ ] Check logs still work

**Deliverables:**
- Test scripts
- Screenshots of successful exploits
- Tool output (sqlmap, Burp)
- Before/after comparisons

---

## PHASE 8: Documentation & Video ⏳
**Status:** Not Started  
**Goal:** Create comprehensive report and demo video

### Report Contents:
- [ ] Executive summary
- [ ] System architecture
- [ ] Vulnerability descriptions (with CWE references)
- [ ] Exploitation methodology
- [ ] Code snippets (vulnerable vs patched)
- [ ] Screenshots of attacks
- [ ] Tool outputs
- [ ] Patch explanations
- [ ] Monitoring system details
- [ ] Testing results

### Video Contents:
- [ ] Application walkthrough
- [ ] Vulnerability demonstrations (all 4)
- [ ] Exploitation using tools
- [ ] Monitoring dashboard showing attacks
- [ ] Patched version blocking attacks
- [ ] Code comparison (vulnerable vs patched)

**Deliverables:**
- Complete report (PDF)
- Demo video
- Code repository with documentation

---

## Final Submission Checklist ⏳
**Status:** Not Started

- [ ] Vulnerable source code + requirements.txt
- [ ] Patched source code + requirements.txt
- [ ] Dockerized vulnerable version
- [ ] Dockerized patched version
- [ ] Database population script
- [ ] Database file (if applicable)
- [ ] Monitoring system functional in both versions
- [ ] Report (PDF)
- [ ] Demo video
- [ ] README with setup instructions
- [ ] All team members listed

---

## Notes & Decisions

### Technology Stack:
- **Backend:** Flask (Python)
- **Database:** SQLite (embedded, OT-friendly, easy Docker deployment)
- **Frontend:** HTML templates + Bootstrap (SCADA-style UI)
- **Container:** Docker + docker-compose
- **Encryption:** AES symmetric encryption (for scenario 3)

### Key Design Decisions:
- Each vulnerability on separate page/endpoint
- Monitoring dashboard: Admin-only access in both versions
- Industrial/SCADA-style UI design
- Clear separation of vulnerable and patched code
- User roles: Admin and Operator only
- File uploads: Firmware updates and valve configuration files

---

**Last Updated:** Dec 28, 2025
**Current Phase:** Phase 1 - COMPLETED ✅
**Next Action:** Phase 2 - Clone to Vulnerable Version

