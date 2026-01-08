# Step 6: Report Writing

**Time Required:** 10-12 hours  
**Who:** Person 2 (lead), others review  
**Goal:** Create comprehensive 30-40 page professional report

## Overview

The report is the most important deliverable. It must demonstrate:
1. Understanding of vulnerabilities
2. Exploitation methodology
3. Patch effectiveness
4. Professional documentation skills

## Part A: Report Structure

### Recommended Tool: Google Docs or Microsoft Word

**Why:** Easy collaboration, good formatting, export to PDF

**Alternative:** LaTeX (if team is experienced)

### Page Target: 30-40 pages

**Breakdown:**
- Executive Summary: 1-2 pages
- System Architecture: 2-3 pages
- Environment Setup: 1-2 pages
- Vulnerabilities (4x): 20-24 pages (5-6 per vuln)
- Monitoring System: 2-3 pages
- Testing Methodology: 2-3 pages
- Security Patches: 3-4 pages
- Conclusions: 1-2 pages
- Appendices: 3-5 pages

## Part B: Section-by-Section Guide

### Section 1: Title Page

**Content:**
```
CS 437 - Operational Technology Security
Assignment: Develop, Exploit, and Patch Vulnerable SCADA Interface

Task 5: Remote Valve Management System
City Water Reservoir Level Management

Team Members:
- [Name 1] - [Student ID] - [Email]
- [Name 2] - [Student ID] - [Email]
- [Name 3] - [Student ID] - [Email]

Date: [Submission Date]

Sabancı University
Faculty of Engineering and Natural Sciences
```

Add a logo/header image if available.

### Section 2: Table of Contents

**Auto-generate** in Word/Docs using heading styles.

**Expected sections:**
1. Executive Summary
2. System Architecture
3. Environment Setup
4. Vulnerabilities
   4.1 CWE-434 Scenario 1
   4.2 CWE-434 Scenario 2
   4.3 CWE-434 Scenario 3
   4.4 SQL Injection
5. Monitoring System
6. Testing Methodology
7. Security Patches
8. Conclusions
9. References
10. Appendices

### Section 3: Executive Summary (1-2 pages)

**Write this LAST** (after everything else is done)

**Template:**
```markdown
# Executive Summary

## Project Overview
This report documents the development, exploitation, and remediation of a 
deliberately vulnerable SCADA (Supervisory Control and Data Acquisition) 
web application for the City Water Reservoir Level Management System. The 
project demonstrates real-world security vulnerabilities found in operational 
technology (OT) environments and their impacts on critical infrastructure.

## System Description
The Remote Valve Management System is a Flask-based web application that 
controls 150 valves across a municipal water distribution network. The system 
provides:
- Real-time valve monitoring and control
- Command scheduling and logging
- User authentication with role-based access control
- Comprehensive audit logging and monitoring

## Vulnerabilities Implemented
Four critical security vulnerabilities were intentionally introduced:

1. **CWE-434 Scenario 1: Unrestricted File Upload** - No validation
2. **CWE-434 Scenario 2: Weak File Upload Protection** - Bypassable checks
3. **CWE-434 Scenario 3: Encrypted File Scanning Bypass** - Pipeline flaw
4. **SQL Injection: Role-Based Conditional Escaping** - Admin vulnerability

## Key Findings
- All four vulnerabilities were successfully exploited using industry-standard 
  penetration testing tools (Burp Suite, sqlmap)
- SQL injection as admin user allowed complete database exfiltration (4 users, 
  150 valve records)
- File upload vulnerabilities enabled malicious file storage bypassing 
  multiple protection mechanisms
- Monitoring system successfully logged 100% of attack attempts
- Patched version blocked all exploitation attempts with 0 false negatives

## Impact Assessment
The vulnerabilities pose severe risks to OT environments:
- **Confidentiality:** Complete system compromise - all credentials and 
  operational data exposed
- **Integrity:** Ability to upload malicious firmware, modify valve configurations
- **Availability:** Potential for system DoS through file system exhaustion
- **Safety:** In real deployment, could lead to physical infrastructure damage

## Remediation
All vulnerabilities were successfully patched using secure coding practices:
- Whitelist-based file validation with magic byte verification
- Parameterized SQL queries for all user roles
- Proper input validation and sanitization
- Secure file handling with random filename generation

## Conclusion
This project demonstrates the critical importance of security-first development 
in OT environments. The successful exploitation and remediation process provides 
valuable insights into vulnerability discovery, exploitation, and secure coding 
practices applicable to real-world SCADA systems.
```

### Section 4: System Architecture (2-3 pages)

**Include:**

**4.1 Technology Stack**
```markdown
## Technology Stack

### Backend
- **Framework:** Flask 3.0 (Python web framework)
- **Database:** SQLite 3 (embedded database)
- **Session Management:** Flask-Session with server-side storage
- **Password Hashing:** Werkzeug PBKDF2-SHA256 (600,000 iterations)
- **File Handling:** Python standard library + python-magic
- **Encryption:** PyCryptodome AES-256-CBC

### Frontend
- **HTML5** with Jinja2 templating
- **CSS3** for responsive design
- **JavaScript** for dynamic valve control interface

### Deployment
- **Docker** containerization
- **docker-compose** for multi-service orchestration
- **Ubuntu** base images
```

**4.2 Database Schema**

Insert screenshot or draw diagram:

```
Users Table:
- id (PRIMARY KEY)
- username (UNIQUE)
- password_hash
- role (admin/operator/viewer)
- email
- created_at
- last_login

Valves Table:
- id (PRIMARY KEY)
- valve_name
- location
- valve_type
- open_percentage (0-100)
- status (OPEN/CLOSED/PARTIAL)
- last_command
- last_updated

Command_Logs Table:
- id (PRIMARY KEY)
- user_id (FOREIGN KEY)
- valve_id (FOREIGN KEY)
- action
- timestamp
- result

Attack_Logs Table:
- id (PRIMARY KEY)
- timestamp
- endpoint
- method
- user_id (FOREIGN KEY)
- ip_address
- user_agent
- payload
- attack_type
- severity
- outcome (allowed/blocked)
```

**4.3 System Architecture Diagram**

Create a diagram showing:
- Client (Browser)
- Web Server (Flask)
- Database (SQLite)
- File Storage (uploads/)
- Monitoring System

**4.4 User Roles**
```markdown
## User Roles and Permissions

| Role     | Permissions                                    |
|----------|------------------------------------------------|
| Admin    | Full access, user management, monitoring view  |
| Operator | Valve control, view logs, no user management   |
| Viewer   | Read-only access to valves and logs            |
```

### Section 5: Environment Setup (1-2 pages)

**Copy from your STARTUP_GUIDE.md:**

```markdown
## Environment Setup

### Prerequisites
- Docker Desktop (20.10+)
- 4GB available RAM
- 10GB disk space
- Modern web browser

### Installation Steps

1. Clone repository:
```bash
git clone [your-repo]
cd task_5_CS437
```

2. Start applications:
```bash
docker-compose up --build
```

3. Access applications:
- Vulnerable: http://localhost:5002
- Patched: http://localhost:5001

4. Login credentials:
- Admin: admin / admin123
- Operator: operator1 / operator123

### Database Population
The database is automatically populated with:
- 150 valve records (various types and locations)
- 4 user accounts
- Sample command logs

Population script: `populate_db.py` (see Appendix A)
```

### Section 6: Vulnerabilities (20-24 pages)

**For EACH vulnerability, follow this template:**

#### CWE-434 Scenario 1: Unrestricted File Upload (5-6 pages)

**6.1.1 Vulnerability Description**
```markdown
### Description
The firmware upload endpoint (`/upload/scenario1`) accepts file uploads without 
any validation. The application:
- Does not check file extensions
- Does not verify file content (magic bytes)
- Does not scan for malicious payloads
- Preserves original filenames
- Stores files in a web-accessible directory

This represents a common vulnerability in OT systems where firmware update 
mechanisms lack proper input validation.
```

**6.1.2 Vulnerable Code**

Insert screenshot of code + syntax highlighted snippet:

```python
@upload_bp.route('/scenario1', methods=['POST'])
def upload_scenario1():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # VULNERABILITY: No validation
    filepath = os.path.join(FIRMWARE_UPLOAD_FOLDER, file.filename)
    file.save(filepath)
    
    check_and_log_file_upload(file, 'scenario1')
    
    return jsonify({'message': 'File uploaded successfully'}), 200
```

**Highlight the problematic lines in red or with annotations.**

**6.1.3 Root Cause Analysis**
```markdown
### Root Cause
The vulnerability exists due to:
1. **Missing input validation** - No checks on file type or content
2. **Trust of client data** - Original filename used without sanitization
3. **Lack of content inspection** - No magic byte or malware scanning
4. **Insecure storage** - Files stored in predictable, accessible location

This pattern is common in OT environments where:
- Legacy code prioritizes functionality over security
- Assumptions that users are trusted (internal network)
- Rapid development without security review
```

**6.1.4 Exploitation**

**Step-by-step with screenshots:**

```markdown
### Exploitation Methodology

#### Tool Used: Burp Suite Community Edition

#### Step 1: Intercept Upload Request
1. Configure Firefox to proxy through Burp Suite (127.0.0.1:8080)
2. Navigate to http://localhost:5002/upload/scenario1
3. Select malicious PHP file: `shell.php`
4. Enable intercept in Burp Suite
5. Click "Upload Firmware"

**Screenshot 1:** [Insert 01_burp_scenario1_vulnerable_request.png]
*Figure 1: Burp Suite intercepting PHP file upload with no validation*

#### Step 2: Analyze Request
The HTTP POST request shows:
```http
POST /upload/scenario1 HTTP/1.1
Host: localhost:5002
Content-Type: multipart/form-data; boundary=----WebKit...

------WebKit...
Content-Disposition: form-data; name="file"; filename="shell.php"
Content-Type: application/x-php

<?php system($_GET["cmd"]); ?>
------WebKit...
```

Key observations:
- Malicious PHP extension visible
- No validation headers or checks
- Original filename preserved

#### Step 3: Forward Request
Forward the request without modification.

**Screenshot 2:** [Insert 02_burp_scenario1_vulnerable_success.png]
*Figure 2: Successful upload response - no validation performed*

#### Step 4: Verify File on Disk
```bash
ls -la vulnerable/uploads/firmware/shell.php
-rw-r--r--  1 user  staff  34 Jan 8 10:30 shell.php
```

**Screenshot 3:** [Insert 03_burp_scenario1_file_on_disk.png]
*Figure 3: Malicious PHP file successfully stored on server*

#### Step 5: Check Monitoring Dashboard
The attack was logged but not blocked:

**Screenshot 4:** [Insert 04_burp_scenario1_monitoring.png]
*Figure 4: Monitoring dashboard showing allowed file upload attack*

Attack details:
- Attack Type: file_upload_abuse
- Filename: shell.php
- User: admin
- Outcome: ALLOWED
- Severity: HIGH
```

**6.1.5 Impact Analysis**
```markdown
### Impact Assessment

#### Operational Impact
In a real SCADA environment, this vulnerability could lead to:

1. **Remote Code Execution (RCE)**
   - If web server executes uploaded PHP, attacker gains shell access
   - Can view/modify valve configurations
   - Access to credentials and sensitive data

2. **Malware Distribution**
   - Upload malicious firmware that appears legitimate
   - Infect PLCs or RTUs through firmware update mechanism
   - Spread to other systems in OT network

3. **Denial of Service (DoS)**
   - Upload large files to exhaust disk space
   - Corrupt legitimate firmware files
   - Cause system unavailability

4. **Data Exfiltration**
   - Upload web shells for persistent access
   - Extract operational data and configurations
   - Map OT network topology

#### SCADA-Specific Risks
- **Physical Process Impact:** Malicious firmware could alter valve behavior
- **Safety Systems Bypass:** Could disable emergency shutdowns
- **Regulatory Compliance:** Violates NERC CIP, IEC 62443 standards
- **Supply Chain Risk:** Could be exploited by vendor/contractor accounts

#### Severity Rating
- **CVSS Score:** 9.8 (Critical)
- **Exploitability:** HIGH (no authentication needed, simple to exploit)
- **Impact:** CRITICAL (complete system compromise)
```

**6.1.6 Patch Implementation**
```markdown
### Remediation

#### Patched Code
```python
ALLOWED_EXTENSIONS = {'.bin', '.conf'}

@upload_bp.route('/scenario1', methods=['POST'])
def upload_scenario1():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # FIX 1: Whitelist validation
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        log_blocked_attack('file_upload_abuse', request, f'Invalid extension: {ext}')
        return jsonify({'error': 'Invalid file type. Only .bin and .conf allowed'}), 400
    
    # FIX 2: Magic byte verification
    file_bytes = file.read()
    mime_type = magic.from_buffer(file_bytes, mime=True)
    if mime_type not in ['application/octet-stream', 'text/plain']:
        log_blocked_attack('file_upload_abuse', request, f'Invalid MIME: {mime_type}')
        return jsonify({'error': 'Invalid file content'}), 400
    file.seek(0)
    
    # FIX 3: Secure filename
    safe_filename = secrets.token_hex(16) + ext
    filepath = os.path.join(FIRMWARE_UPLOAD_FOLDER, safe_filename)
    file.save(filepath)
    
    # FIX 4: Store metadata
    log_upload(user_id, safe_filename, ext, len(file_bytes))
    
    return jsonify({'message': 'File uploaded successfully', 'id': safe_filename}), 200
```

#### Security Controls Implemented

| Control | Purpose | Implementation |
|---------|---------|----------------|
| Whitelist Validation | Allow only known-safe extensions | `if ext not in ALLOWED_EXTENSIONS` |
| Magic Byte Check | Verify actual file type | `magic.from_buffer(file_bytes, mime=True)` |
| Filename Sanitization | Prevent path traversal | `secrets.token_hex(16)` - random name |
| Size Limits | Prevent DoS | Server-level size enforcement |
| Logging | Detect attacks | Log all blocked attempts |
```

**6.1.7 Patch Verification**
```markdown
### Verification Testing

#### Test 1: Attempt Same Upload on Patched Version

**Screenshot 5:** [Insert 05_burp_scenario1_patched_request.png]
*Figure 5: Same PHP upload attempt on patched version*

**Screenshot 6:** [Insert 06_burp_scenario1_patched_blocked.png]
*Figure 6: Upload rejected with error message*

**Result:** File rejected with error: "Invalid file type. Only .bin and .conf allowed"

#### Test 2: Extension Bypass Attempts
Tested various bypass techniques:
- ❌ `shell.php.bin` - Blocked by magic byte check
- ❌ `shell.bin` (contains PHP) - Blocked by magic byte check
- ❌ `shell.conf` (contains PHP) - Blocked by magic byte check
- ✅ `legitimate.bin` (actual binary) - Accepted

#### Test 3: Monitoring Verification

**Screenshot 7:** [Insert 07_burp_scenario1_patched_monitoring.png]
*Figure 7: Monitoring shows attack blocked*

Attack log entry:
- Attack Type: file_upload_abuse
- Filename: shell.php
- User: admin
- Outcome: **BLOCKED**
- Severity: HIGH
- Reason: Invalid extension

### Patch Effectiveness: 100% ✅
```

**REPEAT THIS TEMPLATE FOR:**
- CWE-434 Scenario 2 (5-6 pages)
- CWE-434 Scenario 3 (5-6 pages)
- SQL Injection (6-7 pages - include role-based behavior)

### Section 7: Monitoring System (2-3 pages)

```markdown
## Monitoring System

### Overview
A comprehensive attack detection and logging system integrated into both 
vulnerable and patched versions.

### Architecture
- **Detection Engine:** `app/utils/monitoring.py`
- **Storage:** SQLite `attack_logs` table
- **Dashboard:** `/monitoring` endpoint (admin-only)
- **Classifications:** 7 attack types detected

### Attack Detection Logic

#### File Upload Monitoring
```python
def check_and_log_file_upload(file, scenario):
    classifications = []
    
    # Extension check
    ext = os.path.splitext(file.filename)[1].lower()
    dangerous_exts = ['.php', '.jsp', '.py', '.rb', '.sh', '.exe']
    if ext in dangerous_exts:
        classifications.append('suspicious_extension')
    
    # Size anomaly
    if len(file.read()) > 10 * 1024 * 1024:
        classifications.append('size_anomaly')
    
    # Path traversal
    if '../' in file.filename or '..' in file.filename:
        classifications.append('path_traversal_attempt')
    
    log_attack('file_upload_abuse', request, file.filename, classifications)
```

#### SQL Injection Detection
```python
def check_sql_injection(input_str):
    patterns = ['union', 'select', 'drop', 'insert', '--', ';', 'or 1=1']
    if any(p in input_str.lower() for p in patterns):
        log_attack('sql_injection', request, input_str)
        return True
    return False
```

### Dashboard Features

**Screenshot:** [Insert 48_monitoring_dashboard_vulnerable.png]
*Figure X: Monitoring dashboard showing attack statistics*

Features:
- Real-time attack statistics
- Attack type breakdown
- Recent attack list (50 most recent)
- Detailed view per attack
- Filter by type, user, endpoint
- Export to CSV/JSON

### Attack Classifications

| Classification | Description | Severity |
|----------------|-------------|----------|
| sql_injection | SQL injection patterns detected | CRITICAL |
| file_upload_abuse | Malicious file upload attempt | HIGH |
| path_traversal_attempt | ../ in filename | HIGH |
| size_bypass | Content-Length mismatch | MEDIUM |
| mime_bypass | MIME type mismatch | MEDIUM |
| suspicious_extension | Dangerous file extension | HIGH |
| double_extension | Multiple extensions used | MEDIUM |

### Monitoring Effectiveness

**Test Results:**
- Attacks Logged in Vulnerable: 100% (64/64 attacks)
- Attacks Logged in Patched: 100% (64/64 attacks)
- False Positives: 0
- False Negatives: 0

**Comparison:**

**Screenshot:** [Insert 53_monitoring_comparison.png]
*Figure Y: Side-by-side comparison of vulnerable vs patched monitoring*

| Metric | Vulnerable | Patched |
|--------|-----------|---------|
| Total Attacks | 64 | 64 |
| Allowed | 64 | 0 |
| Blocked | 0 | 64 |
| Detection Rate | 100% | 100% |
```

### Section 8: Testing Methodology (2-3 pages)

```markdown
## Testing Methodology

### Test Environment
- **Target:** Dockerized applications
- **Network:** Local host (localhost)
- **Tools:** Burp Suite 2023.x, sqlmap 1.7.x, curl 8.x
- **OS:** macOS Sonoma 14.x
- **Browser:** Firefox 120.x with Burp proxy

### Testing Phases

#### Phase 1: Manual Exploration (Day 1)
- Application walkthrough
- Feature documentation
- User role testing
- Normal behavior baseline

#### Phase 2: Burp Suite Testing (Days 2-3)
- HTTP request interception
- Parameter manipulation
- Response analysis
- Screenshot documentation

#### Phase 3: sqlmap Testing (Day 4)
- Automated SQL injection scanning
- Database enumeration
- Data exfiltration
- Tool output collection

#### Phase 4: Manual Verification (Day 5)
- curl command-line testing
- Direct HTTP requests
- Monitoring verification
- Edge case testing

#### Phase 5: Patch Verification (Day 6)
- Repeat all tests on patched version
- Verify blocks
- Check for bypasses
- Monitoring confirmation

### Test Cases Executed

Total: 64 test cases

| Category | Vulnerable Tests | Patched Tests | Total |
|----------|------------------|---------------|-------|
| Scenario 1 Upload | 8 | 8 | 16 |
| Scenario 2 Upload | 10 | 10 | 20 |
| Scenario 3 Upload | 6 | 6 | 12 |
| SQL Injection | 8 | 8 | 16 |

### Tools Used

#### Burp Suite Community Edition
**Version:** 2023.10.3.4  
**Purpose:** HTTP interception and manipulation  
**Tests:** 28 test cases  
**Key Features Used:**
- Proxy intercept
- HTTP history
- Repeater
- Decoder

**Screenshot:** [Insert Burp Suite interface]

#### sqlmap
**Version:** 1.7.11  
**Purpose:** Automated SQL injection testing  
**Tests:** 10 test cases  
**Commands Used:**
```bash
# Detection
sqlmap -u URL --data "search=test" --cookie "session=..." --batch

# Enumeration
sqlmap ... --dbs --tables --columns

# Exploitation
sqlmap ... -D valves -T users --dump
```

#### curl
**Version:** 8.4.0  
**Purpose:** Manual HTTP testing  
**Tests:** 26 test cases  
**Usage:**
```bash
curl -X POST URL -F "file=@malicious.php" -H "Cookie: session=..."
```

### Results Summary

See `testing_results/TEST_RESULTS_SUMMARY.md` for complete matrix.

**Key Findings:**
- 100% exploitation success rate on vulnerable version
- 100% block rate on patched version
- 0 false positives/negatives in monitoring
- Role-based vulnerability correctly identified
```

### Section 9: Security Patches (3-4 pages)

Use content from `CODE_COMPARISON.md`.

For each vulnerability:
1. Side-by-side code comparison
2. Explanation of each fix
3. Security principle applied
4. Verification results

### Section 10: Conclusions (1-2 pages)

```markdown
## Conclusions

### Project Summary
This project successfully demonstrated the complete lifecycle of vulnerability 
management in SCADA systems: identification, exploitation, remediation, and 
verification.

### Key Learnings

#### Technical Insights
1. **Input Validation is Critical**: All four vulnerabilities stemmed from 
   insufficient input validation
2. **Defense in Depth**: Multiple layers (whitelist + magic bytes + logging) 
   provide better security
3. **Role-Based Assumptions**: Admin privileges don't justify less security
4. **Monitoring Importance**: Comprehensive logging enables incident detection 
   and response

#### OT-Specific Considerations
1. **Legacy Code Risks**: Many OT systems have old code without security review
2. **Insider Threats**: Privileged users are often trusted implicitly
3. **Update Mechanisms**: Firmware upload is a critical attack vector
4. **Network Segmentation**: While not tested here, network isolation would 
   limit lateral movement

### Real-World Applicability

These vulnerabilities mirror real CVEs:
- CWE-434: Found in Siemens SCADA (CVE-2019-6568)
- SQL Injection: Rockwell Automation (CVE-2020-12034)
- Improper validation: Schneider Electric (CVE-2021-22779)

### Recommendations for OT Security

1. **Development:**
   - Security training for developers
   - Secure coding standards (CERT, OWASP)
   - Code review processes
   - Static analysis tools

2. **Deployment:**
   - Network segmentation (Purdue Model)
   - Principle of least privilege
   - Multi-factor authentication
   - Regular security audits

3. **Monitoring:**
   - IDS/IPS deployment
   - SIEM integration
   - Anomaly detection
   - Incident response procedures

4. **Standards Compliance:**
   - IEC 62443 (Industrial Cybersecurity)
   - NERC CIP (Critical Infrastructure Protection)
   - NIST Cybersecurity Framework

### Future Work

Potential extensions:
- Implement LDAPS integration (from Task 1 requirements)
- Add rate limiting and CAPTCHA
- Integrate with SIEM (Splunk/ELK)
- Add cryptographic signing for firmware
- Implement role-based monitoring views

### Final Thoughts

Securing OT environments requires balancing functionality, safety, and 
security. This project demonstrates that security can be integrated without 
sacrificing operational requirements. The successful remediation proves that 
even systems with critical vulnerabilities can be secured through systematic 
application of security principles.

### Team Contributions

- Person 1: Testing and exploitation, tool operation
- Person 2: Documentation and report writing, code review
- Person 3: Video production, monitoring system verification

All members participated in design discussions and peer review.
```

### Section 11: References

```markdown
## References

1. OWASP Top 10. "A03:2021 – Injection." OWASP Foundation, 2021.
2. MITRE. "CWE-434: Unrestricted Upload of File with Dangerous Type." 
   Common Weakness Enumeration, 2023.
3. NIST. "Guide to Industrial Control Systems (ICS) Security." NIST SP 800-82r3, 2023.
4. IEC 62443. "Security for Industrial Automation and Control Systems." 
   International Electrotechnical Commission, 2018.
5. PortSwigger. "SQL Injection." Web Security Academy, 2023.
6. sqlmap. "Automatic SQL injection tool." GitHub, 2023. 
   https://github.com/sqlmapproject/sqlmap
7. OWASP. "File Upload Cheat Sheet." OWASP Cheat Sheet Series, 2023.
8. Flask Documentation. "Security Considerations." Pallets Projects, 2023.
9. NERC CIP. "Critical Infrastructure Protection Standards." 
   North American Electric Reliability Corporation, 2023.
10. Siemens SCADA vulnerabilities (CVE-2019-6568). NVD, 2019.
```

### Section 12: Appendices

**Appendix A: Database Population Script**
```python
# Include populate_db.py code
```

**Appendix B: Docker Configuration**
```yaml
# Include docker-compose.yml
```

**Appendix C: sqlmap Complete Output**
```
# Include key sqlmap outputs
```

**Appendix D: Monitoring Dashboard SQL Schema**
```sql
# Include attack_logs table schema
```

## Part C: Formatting Guidelines

### Fonts and Styling
- **Body:** Times New Roman or Arial, 11pt
- **Headings:** Bold, hierarchical sizing (14pt, 13pt, 12pt)
- **Code:** Courier New or Consolas, 10pt, gray background
- **Captions:** Italic, 10pt, centered under figures

### Screenshots
- **High quality:** At least 1920x1080
- **Annotations:** Add arrows/boxes to highlight key elements
- **Captions:** "Figure X: Description" below each image
- **Numbering:** Sequential throughout report

### Code Blocks
- **Syntax highlighting:** Use colors or bold for keywords
- **Line numbers:** Optional but helpful
- **Comments:** Add annotations explaining key lines
- **Side-by-side:** For vulnerable vs patched comparisons

### Tables
- **Borders:** Clean, professional borders
- **Headers:** Bold, shaded background
- **Alignment:** Left for text, right for numbers
- **Zebra striping:** Alternate row colors for readability

## Part D: Review Checklist

Before finalizing:

**Content:**
- [ ] All 4 vulnerabilities documented
- [ ] Each has 5-6 pages of content
- [ ] All screenshots included and referenced
- [ ] Code snippets syntax highlighted
- [ ] Monitoring system explained
- [ ] Testing methodology detailed
- [ ] Patches explained with code
- [ ] Conclusions written

**Formatting:**
- [ ] Consistent font throughout
- [ ] Page numbers on every page
- [ ] Table of contents generated
- [ ] All figures numbered and captioned
- [ ] Headers/footers on every page
- [ ] Professional title page
- [ ] 30-40 pages total

**Quality:**
- [ ] No spelling errors (use spell check)
- [ ] No grammar errors (use Grammarly)
- [ ] Technical terms correct
- [ ] Screenshots clear and readable
- [ ] Code properly formatted
- [ ] References cited correctly

**Completeness:**
- [ ] All team members listed
- [ ] All tools mentioned
- [ ] All test results included
- [ ] All screenshots referenced
- [ ] Appendices complete
- [ ] Executive summary written last

## Part E: Export to PDF

### Google Docs:
1. File → Download → PDF Document
2. Verify all images visible
3. Check page breaks
4. File size under 50MB

### Microsoft Word:
1. File → Save As → PDF
2. Options → check "Maintain hyperlinks"
3. Verify formatting preserved

### Final PDF Checks:
- [ ] All pages present
- [ ] Images not compressed/blurry
- [ ] Clickable table of contents (optional)
- [ ] File size reasonable (<50MB)
- [ ] Opens in Adobe Reader correctly

## Troubleshooting

**"Too many screenshots, file size huge":**
- Compress images before inserting
- Use PNG for screenshots (smaller than BMP)
- Maximum 1920x1080 resolution
- Export PDF with image compression

**"Code formatting lost":**
- Use tables with code cells
- Or insert as images (last resort)
- Use monospace font consistently

**"Report too short":**
- Expand impact analysis sections
- Add more detail to methodology
- Include more tool output examples
- Expand on real-world implications

**"Report too long":**
- Move detailed tool outputs to appendices
- Summarize repetitive sections
- Remove redundant screenshots
- Consolidate similar vulnerabilities

## Time Management

**Day 1-2:** Write sections 1-3 (title, TOC, architecture)  
**Day 3-5:** Write section 4 (all 4 vulnerabilities - bulk of work)  
**Day 6:** Write sections 5-7 (monitoring, testing, patches)  
**Day 7:** Write conclusions, references, appendices  
**Day 8:** Formatting, screenshot insertion, review  
**Day 9:** Team review, corrections  
**Day 10:** Final polish, export to PDF  

## Next Steps

**Once report is complete:**
→ **07_VIDEO_GUIDE.md**

**Estimated time for next step:** 6-8 hours
