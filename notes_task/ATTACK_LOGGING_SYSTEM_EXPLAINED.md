# Attack Logging System - Complete Explanation

## Table of Contents
1. [System Architecture](#system-architecture)
2. [Database Structure](#database-structure)
3. [Attack Detection Mechanisms](#attack-detection-mechanisms)
4. [Attack Logging Process](#attack-logging-process)
5. [Automated Response System](#automated-response-system)
6. [Viewing and Managing Logs](#viewing-and-managing-logs)
7. [Attack Types and Examples](#attack-types-and-examples)
8. [Complete Flow Diagrams](#complete-flow-diagrams)

---

## System Architecture

The attack logging system consists of 4 main components:

```
┌─────────────────────────────────────────────────────────────────┐
│                         REQUEST LAYER                            │
│  Every HTTP request passes through security middleware first     │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DETECTION LAYER                               │
│  monitoring.py - Pattern matching, behavioral analysis           │
│  - SQL injection patterns                                        │
│  - XSS patterns                                                  │
│  - Path traversal                                                │
│  - File upload abuse                                             │
│  - Brute force detection                                         │
│  - Rate limiting                                                 │
│  - Session anomalies                                             │
│  - Privilege escalation                                          │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                     LOGGING LAYER                                │
│  models.py - AttackLog.create()                                  │
│  - Stores comprehensive attack data                              │
│  - Calculates risk scores                                        │
│  - Classifies attack types                                       │
│  - Recommends actions                                            │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                   AUTO-RESPONSE LAYER                            │
│  auto_response.py - Automated security actions                   │
│  - Block IP addresses                                            │
│  - Lock user accounts                                            │
│  - Rate limiting                                                 │
│  - Alert administrators                                          │
└─────────────────────────────────────────────────────────────────┘
```

---

## Database Structure

### attack_logs Table Schema

The `attack_logs` table is the central storage for all security incidents:

```sql
CREATE TABLE attack_logs (
    -- Primary Key
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Attack Classification
    attack_type TEXT NOT NULL,  -- Type of attack detected
    severity TEXT,              -- low, medium, high, critical
    classification TEXT,        -- reconnaissance/exploitation/post_exploitation
    
    -- Request Information
    endpoint TEXT NOT NULL,     -- Which URL was targeted
    request_method TEXT,        -- GET, POST, PUT, DELETE, etc.
    payload TEXT,               -- The malicious input/data
    
    -- Attacker Information
    user_id INTEGER,            -- If authenticated
    ip_address TEXT,            -- Source IP
    user_agent TEXT,            -- Browser/tool identifier
    geolocation TEXT,           -- Geographic location
    
    -- Security Analysis
    risk_score INTEGER,         -- 0-100 calculated risk level
    blocked BOOLEAN,            -- Was request blocked?
    details TEXT,               -- Human-readable description
    
    -- Response Management
    recommended_action TEXT,    -- Suggested response
    action_taken TEXT,          -- What action was performed
    action_reversible BOOLEAN,  -- Can action be undone?
    reverse_action_steps TEXT,  -- How to reverse (JSON)
    
    -- Forensics & Correlation
    raw_request_data TEXT,      -- Full request details (JSON)
    response_status INTEGER,    -- HTTP response code
    related_attack_id INTEGER,  -- Links multi-stage attacks
    
    -- Metadata
    timestamp TIMESTAMP,        -- When attack occurred
    
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (related_attack_id) REFERENCES attack_logs(id)
)
```

### Supported Attack Types

```python
attack_types = [
    'sql_injection',           # SQL code injection
    'xss_attempt',            # Cross-site scripting
    'path_traversal',         # Directory traversal
    'file_upload_abuse',      # Malicious file uploads
    'size_bypass',            # File size limit bypass
    'mime_bypass',            # MIME type filtering bypass
    'encrypted_payload',      # Encrypted malicious content
    'login_brute_force',      # Password guessing
    'directory_brute_force',  # Directory enumeration
    'session_hijacking',      # Session takeover
    'cookie_manipulation',    # Cookie tampering
    'rate_limit_violation',   # Too many requests
    'privilege_escalation',   # Unauthorized access
    'csrf_attempt',           # Cross-site request forgery
    'suspicious_activity',    # Scanning tools detected
    'unauthorized_access'     # Access denied attempts
]
```

---

## Attack Detection Mechanisms

### 1. Pattern-Based Detection

**SQL Injection Detection:**
```python
SQL_INJECTION_PATTERNS = [
    r"(\bUNION\b.*\bSELECT\b)",  # UNION SELECT attacks
    r"(\bOR\b\s+\d+\s*=\s*\d+)",  # OR 1=1 logic bombs
    r"('|\")(\s*OR\s*\1\s*=\s*\1)",  # ' OR '=' attacks
    r"(;|\-\-|\/\*|\*\/)",  # Comment injection
    r"(\bDROP\b|\bDELETE\b|\bINSERT\b|\bUPDATE\b)",  # Dangerous keywords
    r"('.*--)",  # Comment after quote
    r"('\s*;\s*--)",  # Semicolon with comment
]
```

**XSS Detection:**
```python
XSS_PATTERNS = [
    r'<script[^>]*>',  # Script tags
    r'javascript:',    # JavaScript protocol
    r'onerror\s*=',   # Event handlers
    r'onload\s*=',
    r'<iframe[^>]*>',  # Iframe injection
    r'eval\(',         # Code execution
    r'expression\(',   # CSS expressions
]
```

**Path Traversal Detection:**
```python
PATH_TRAVERSAL_PATTERNS = [
    r'\.\.[/\\]',      # ../
    r'\.\.%2[fF]',     # ..%2F (encoded)
    r'%2e%2e[/\\]',    # %2e%2e/ (encoded)
    r'\.\.\\',         # ..\ (Windows)
]
```

### 2. Behavioral Detection

**Rate Limiting:**
- Tracks requests per IP per endpoint
- Threshold: 100 requests per minute
- Uses in-memory tracking with cleanup

**Directory Brute Force:**
- Monitors 404 errors per IP
- Threshold: 20 in 5 minutes
- Detects directory enumeration tools

**Session Anomalies:**
- Tracks IP address per session
- Detects IP changes during session
- Identifies session hijacking

### 3. File Upload Abuse Detection

```python
def detect_file_upload_abuse(filename, content_type, file_size):
    issues = []
    
    # Check for suspicious extensions
    SUSPICIOUS_EXTENSIONS = ['.php', '.jsp', '.asp', '.exe', '.sh', etc.]
    
    # Check for path traversal in filename
    if '..' in filename or '/' in filename:
        issues.append('path_traversal_attempt')
    
    # Check for double extensions (bypass attempt)
    if has_double_extension(filename):
        issues.append('double_extension')
    
    # Check file size
    if file_size > 10MB:
        issues.append('oversized_file')
    
    return issues
```

### 4. User Agent Detection

```python
SUSPICIOUS_USER_AGENTS = [
    'nikto',      # Web scanner
    'sqlmap',     # SQL injection tool
    'nmap',       # Network scanner
    'burp',       # Proxy/scanner
    'metasploit', # Exploitation framework
    'dirbuster',  # Directory brute force
    'gobuster',   # Directory brute force
    'ffuf'        # Fuzzer
]
```

---

## Attack Logging Process

### Step 1: Detection
When an attack pattern is detected, a detection function returns True:

```python
# Example: SQL Injection Detection
search_term = request.form.get('search')
if detect_sql_injection(search_term):
    # Proceed to logging
```

### Step 2: Risk Calculation
Calculate risk score based on multiple factors:

```python
def calculate_risk_score(attack_type, ip_address, user_id, endpoint):
    # Base score by attack type
    base_scores = {
        'sql_injection': 80,
        'privilege_escalation': 90,
        'session_hijacking': 85,
        'file_upload_abuse': 75,
        'login_brute_force': 70,
        # ... more types
    }
    
    risk_score = base_scores.get(attack_type, 50)
    
    # Increase score for repeat offenders
    recent_attacks = AttackLog.get_recent_by_ip(ip_address, minutes=60)
    if len(recent_attacks) > 3:
        risk_score += len(recent_attacks) * 5
    
    # Increase score for admin endpoint targeting
    if is_admin_endpoint(endpoint):
        risk_score += 10
    
    return min(100, risk_score)  # Cap at 100
```

### Step 3: Attack Classification
Classify attack into stages:

```python
def classify_attack(attack_type, endpoint, payload):
    # Stage 1: Reconnaissance
    if attack_type in ['directory_brute_force', 'unauthorized_access']:
        return 'reconnaissance', 'reconnaissance'
    
    # Stage 2: Exploitation
    elif attack_type in ['sql_injection', 'file_upload_abuse', 'xss_attempt']:
        return 'exploitation', 'exploitation'
    
    # Stage 3: Post-Exploitation
    elif attack_type in ['privilege_escalation', 'session_hijacking']:
        return 'post_exploitation', 'post_exploitation'
    
    return 'general_attack', 'unknown'
```

### Step 4: Action Recommendation
Suggest appropriate response:

```python
def recommend_action(attack_type, risk_score, attack_count):
    # Immediate blocking for SQL injection
    if attack_type == 'sql_injection':
        return 'block_ip_permanent', ['Steps to unblock']
    
    # Temporary block for brute force
    elif attack_type == 'login_brute_force' and attack_count >= 5:
        return 'block_ip_temporary', ['Steps to unblock']
    
    # High priority for privilege escalation
    elif attack_type == 'privilege_escalation':
        return 'block_ip_and_alert', ['Steps to investigate']
    
    # Risk-based decisions
    elif risk_score >= 80:
        return 'block_ip_and_alert', ['Steps to review']
    elif risk_score >= 60:
        return 'alert_admin', ['Steps to monitor']
    else:
        return 'log_only', ['No action needed']
```

### Step 5: Log Creation
Store comprehensive attack information:

```python
def log_attack(attack_type, endpoint, payload, severity, blocked=False, 
               details=None, classification=None, recommended_action=None):
    
    # Gather request context
    user_id = session.get('user_id')
    ip_address = request.remote_addr
    user_agent = request.headers.get('User-Agent')
    request_method = request.method
    
    # Calculate metadata
    risk_score = calculate_risk_score(attack_type, ip_address, user_id, endpoint)
    category, stage = classify_attack(attack_type, endpoint, payload)
    classification = f"{category}_{stage}"
    
    # Get recommendation
    recent_count = len(AttackLog.get_recent_by_ip(ip_address, 60))
    action, reverse_steps = recommend_action(attack_type, risk_score, recent_count)
    
    # Capture full request details
    raw_request_data = json.dumps({
        'headers': dict(request.headers),
        'args': dict(request.args),
        'form': dict(request.form),
        'method': request.method,
        'path': request.path,
        'remote_addr': request.remote_addr
    })
    
    # Create database record
    attack_id = AttackLog.create(
        attack_type=attack_type,
        endpoint=endpoint,
        user_id=user_id,
        ip_address=ip_address,
        user_agent=user_agent,
        request_method=request_method,
        payload=payload,
        severity=severity,
        blocked=blocked,
        details=details,
        classification=classification,
        recommended_action=action,
        risk_score=risk_score,
        raw_request_data=raw_request_data,
        reverse_action_steps=json.dumps(reverse_steps)
    )
    
    # Trigger automated response
    check_and_execute_auto_response(attack_id, attack_type, ip_address, 
                                    user_id, risk_score)
    
    return attack_id
```

---

## Automated Response System

### Auto-Response Rules

Rules are stored in the `auto_response_rules` table:

```sql
CREATE TABLE auto_response_rules (
    id INTEGER PRIMARY KEY,
    rule_name TEXT UNIQUE,
    attack_type TEXT,              -- Which attack triggers this
    trigger_condition TEXT,        -- What condition to check
    action_type TEXT,              -- What action to take
    threshold INTEGER,             -- Trigger threshold
    time_window_minutes INTEGER,   -- Time window for counting
    enabled BOOLEAN DEFAULT 1
)
```

### Default Rules

**Rule 1: SQL Injection Auto-Block**
- **Attack Type:** sql_injection
- **Trigger:** 3 attempts in 60 minutes
- **Action:** Block IP for 24 hours
- **Reversible:** Yes

**Rule 2: Login Brute Force Protection**
- **Attack Type:** login_brute_force
- **Trigger:** 5 attempts in 10 minutes
- **Action:** Block IP for 24 hours
- **Reversible:** Yes

**Rule 3: Account Lock on Failed Logins**
- **Attack Type:** login_brute_force
- **Trigger:** 5 failed attempts per username in 15 minutes
- **Action:** Lock account for 2 hours
- **Reversible:** Yes

**Rule 4: Rate Limiting**
- **Attack Type:** rate_limit_violation
- **Trigger:** 100 requests per minute
- **Action:** Temporary block for 30 minutes
- **Reversible:** Yes (automatic)

**Rule 5: Privilege Escalation Immediate Block**
- **Attack Type:** privilege_escalation
- **Trigger:** Any attempt (threshold=1)
- **Action:** Block IP and alert admin
- **Reversible:** Yes (manual)

### Auto-Response Flow

```
Attack Logged
     │
     ▼
Get Enabled Rules for Attack Type
     │
     ▼
For Each Rule:
  ├── Check Trigger Condition
  │   ├── failed_attempts: Count failed logins by IP
  │   ├── failed_login_per_user: Count by username
  │   ├── attack_count: Count specific attack type
  │   ├── requests_per_minute: Count recent requests
  │   └── risk_score: Compare calculated risk
  │
  ▼
  Threshold Met?
  │
  ├─ NO ─→ Continue to next rule
  │
  └─ YES ─→ Execute Action
             │
             ▼
       ┌─────────────────┐
       │   Action Type   │
       └────────┬────────┘
                │
    ┌───────────┼───────────┬──────────┐
    │           │           │          │
    ▼           ▼           ▼          ▼
block_ip   lock_account  rate_limit  alert_admin
```

### Action Execution

**Block IP:**
```python
def execute_block_ip(ip_address, rule, attack_id, attack_type_name):
    # Check if already blocked
    if BlockedIP.is_blocked(ip_address):
        return
    
    # Block for 24 hours
    blocked_until = datetime.now() + timedelta(hours=24)
    
    # Create block record
    BlockedIP.create(
        ip_address=ip_address,
        reason=f"Auto-blocked: {attack_type_name} - Rule: {rule['rule_name']}",
        blocked_until=blocked_until,
        auto_unblock=True,
        attack_log_id=attack_id
    )
    
    # Log security action
    SecurityAction.create(
        action_type='block_ip',
        target=ip_address,
        reason=f"Auto-blocked: {attack_type_name}",
        attack_log_id=attack_id,
        automated=True
    )
    
    # Update attack log
    AttackLog.mark_action_taken(attack_id, 'ip_blocked_auto_24h')
```

**Lock Account:**
```python
def execute_lock_account(user_id, rule, attack_id, attack_type_name):
    # Check if already locked
    if UserLocked.is_locked(user_id):
        return
    
    # Lock for 2 hours
    locked_until = datetime.now() + timedelta(hours=2)
    
    # Create lock record
    UserLocked.lock_user(
        user_id=user_id,
        reason=f"Auto-locked: {attack_type_name} - Rule: {rule['rule_name']}",
        locked_until=locked_until
    )
    
    # Log security action
    SecurityAction.create(
        action_type='lock_account',
        target=f"user_id:{user_id}",
        reason=f"Auto-locked: {attack_type_name}",
        attack_log_id=attack_id,
        automated=True
    )
    
    # Update attack log
    AttackLog.mark_action_taken(attack_id, 'account_locked_auto_2h')
```

---

## Viewing and Managing Logs

### Admin Monitoring Dashboard

**Route:** `/monitoring` (admin only)

**What It Shows:**

1. **Attack Statistics:**
   - Total attacks
   - Attacks by type (pie chart data)
   - Attacks by severity (bar chart data)
   - Recent attacks (last 24 hours)
   - Blocked attacks count
   - Average risk score

2. **Recent Attacks (50 most recent):**
   - Timestamp
   - Attack type
   - IP address
   - Username (if authenticated)
   - Risk score
   - Action taken
   - Details

3. **High-Risk Attacks (risk_score >= 70):**
   - Sorted by risk score descending
   - Prioritized for review

4. **Actionable Attacks:**
   - Attacks with recommended_action != 'log_only'
   - Where no action has been taken yet
   - Requires manual intervention

5. **Blocked IPs:**
   - Currently active blocks
   - Reason for block
   - Block expiration time
   - Unblock button

6. **Locked Accounts:**
   - Currently locked users
   - Reason for lock
   - Lock expiration time
   - Unlock button

7. **Security Actions Log:**
   - All manual and automated actions
   - Who executed them
   - When they were executed
   - If they were reversed

8. **Auto-Response Rules:**
   - Active/inactive status
   - Thresholds
   - Toggle enable/disable

### API Endpoints for Logs

**Get Attack Statistics:**
```http
GET /api/monitoring/stats
Authorization: Admin required

Response:
{
  "total_attacks": 1234,
  "by_type": [
    {"attack_type": "sql_injection", "count": 45},
    {"attack_type": "login_brute_force", "count": 89}
  ],
  "by_severity": [
    {"severity": "critical", "count": 12},
    {"severity": "high", "count": 234}
  ],
  "recent_24h": 156,
  "blocked_count": 89,
  "avg_risk_score": 65.4
}
```

**Get Attacks (Filtered):**
```http
GET /api/monitoring/attacks?type=sql_injection&limit=100
GET /api/monitoring/attacks?risk_threshold=70&limit=50

Response:
[
  {
    "id": 123,
    "attack_type": "sql_injection",
    "endpoint": "/valves/search",
    "ip_address": "192.168.1.100",
    "username": "attacker",
    "payload": "' OR 1=1--",
    "severity": "high",
    "risk_score": 85,
    "blocked": true,
    "action_taken": "ip_blocked_auto_24h",
    "timestamp": "2026-01-14 10:30:45"
  }
]
```

**Get Actionable Attacks:**
```http
GET /api/monitoring/actionable

Response: List of attacks requiring manual action
```

**Get Attack Details with Chain:**
```http
GET /api/security/attack-details/123

Response:
{
  "attack": { ... attack details ... },
  "related_attacks": [ ... multi-stage attack chain ... ]
}
```

### Database Queries for Logs

**View All Recent Attacks:**
```sql
SELECT al.*, u.username 
FROM attack_logs al
LEFT JOIN users u ON al.user_id = u.id
ORDER BY al.timestamp DESC 
LIMIT 100;
```

**View High-Risk Attacks:**
```sql
SELECT al.*, u.username 
FROM attack_logs al
LEFT JOIN users u ON al.user_id = u.id
WHERE al.risk_score >= 70
ORDER BY al.risk_score DESC, al.timestamp DESC;
```

**View Attacks by IP:**
```sql
SELECT * FROM attack_logs 
WHERE ip_address = '192.168.1.100'
ORDER BY timestamp DESC;
```

**View Attacks by Type:**
```sql
SELECT * FROM attack_logs 
WHERE attack_type = 'sql_injection'
ORDER BY timestamp DESC;
```

**View Attacks Requiring Action:**
```sql
SELECT al.*, u.username 
FROM attack_logs al
LEFT JOIN users u ON al.user_id = u.id
WHERE al.recommended_action IS NOT NULL 
  AND al.recommended_action != 'log_only'
  AND (al.action_taken IS NULL OR al.action_taken = '')
ORDER BY al.risk_score DESC;
```

**View Attack Chains:**
```sql
SELECT * FROM attack_logs 
WHERE related_attack_id = 123 OR id = 123
ORDER BY timestamp;
```

---

## Attack Types and Examples

### 1. SQL Injection

**Detection:**
```python
search_term = request.form.get('search')
if detect_sql_injection(search_term):
    log_attack(...)
```

**Example Payloads:**
- `' OR 1=1--`
- `' UNION SELECT * FROM users--`
- `admin'--`
- `'; DROP TABLE users--`

**Logged Information:**
```json
{
  "attack_type": "sql_injection",
  "endpoint": "/valves/search",
  "payload": "' OR 1=1--",
  "severity": "high",
  "blocked": true,
  "details": "SQL injection pattern detected in search query",
  "risk_score": 85,
  "classification": "exploitation_exploitation",
  "recommended_action": "block_ip_permanent"
}
```

### 2. Login Brute Force

**Detection:**
```python
# On failed login
user = User.authenticate(username, password)
if not user:
    attack_id = log_attack(
        attack_type='login_brute_force',
        endpoint='/login',
        payload=f'username: {username}',
        severity='medium',
        blocked=False
    )
    
    FailedLoginTracker.create(username, ip_address, attack_id)
```

**Example Scenario:**
- Attacker tries 10 passwords for "admin"
- After 5 failures: Account locked
- After 10 failures: IP blocked

**Logged Information:**
```json
{
  "attack_type": "login_brute_force",
  "endpoint": "/login",
  "payload": "username: admin",
  "severity": "medium",
  "blocked": false,
  "details": "Failed login attempt for user: admin",
  "risk_score": 70,
  "classification": "exploitation_exploitation",
  "recommended_action": "block_ip_temporary"
}
```

### 3. File Upload Abuse

**Detection:**
```python
filename = secure_filename(file.filename)
issues = detect_file_upload_abuse(filename, content_type, file_size)

if issues:
    log_attack(
        attack_type='file_upload_abuse',
        endpoint='/upload/secure',
        payload=f'filename:{filename}, size:{file_size}',
        severity='high',
        blocked=True,
        details=', '.join(issues)
    )
```

**Example Payloads:**
- `malicious.php` (suspicious extension)
- `shell.php.bin` (double extension)
- `../../../evil.bin` (path traversal)
- 15MB file (oversized)

**Logged Information:**
```json
{
  "attack_type": "file_upload_abuse",
  "endpoint": "/upload/secure",
  "payload": "filename:shell.php, size:1024, type:application/octet-stream",
  "severity": "high",
  "blocked": true,
  "details": "suspicious_extension:.php",
  "risk_score": 80,
  "classification": "exploitation_exploitation",
  "recommended_action": "block_ip_permanent"
}
```

### 4. Privilege Escalation

**Detection:**
```python
# In security middleware
if user_role == 'operator' and '/admin' in endpoint:
    log_attack(
        attack_type='privilege_escalation',
        endpoint=endpoint,
        payload=f'Role: {user_role}',
        severity='critical',
        blocked=True,
        details=f'Operator attempting to access admin endpoint'
    )
```

**Example Scenario:**
- Operator user tries to access `/monitoring`
- Immediately blocked
- IP address blocked
- Admin alerted

**Logged Information:**
```json
{
  "attack_type": "privilege_escalation",
  "endpoint": "/monitoring",
  "user_id": 2,
  "payload": "Role: operator",
  "severity": "critical",
  "blocked": true,
  "details": "Operator attempting to access admin endpoint: /monitoring",
  "risk_score": 90,
  "classification": "post_exploitation_post_exploitation",
  "recommended_action": "block_ip_and_alert"
}
```

### 5. Session Hijacking

**Detection:**
```python
# In security middleware
session_ip = session.get('ip_address')
current_ip = request.remote_addr

if session_ip and session_ip != current_ip:
    log_attack(
        attack_type='session_hijacking',
        endpoint=request.path,
        payload=f'User ID: {user_id}',
        severity='high',
        blocked=True,
        details=f'IP changed from {session_ip} to {current_ip}'
    )
```

**Example Scenario:**
- User logs in from 192.168.1.100
- Session cookie stolen
- Attacker uses cookie from 10.0.0.50
- Session terminated, attack logged

**Logged Information:**
```json
{
  "attack_type": "session_hijacking",
  "endpoint": "/dashboard",
  "user_id": 1,
  "ip_address": "10.0.0.50",
  "payload": "User ID: 1",
  "severity": "high",
  "blocked": true,
  "details": "IP changed from 192.168.1.100 to 10.0.0.50",
  "risk_score": 85,
  "classification": "post_exploitation_post_exploitation",
  "recommended_action": "block_ip_and_alert"
}
```

### 6. Directory Brute Force

**Detection:**
```python
# On 404 errors
def log_404_handler(error):
    ip_address = request.remote_addr
    is_brute_force, count = detect_directory_brute_force(ip_address)
    
    if is_brute_force and count % 20 == 0:
        log_attack(
            attack_type='directory_brute_force',
            endpoint=path,
            payload=f'{count} 404 errors in 5 minutes',
            severity='medium',
            blocked=False
        )
```

**Example Scenario:**
- Attacker runs dirb/gobuster
- Generates 50 404 errors in 2 minutes
- Attack logged every 20 attempts
- Can trigger rate limiting

**Logged Information:**
```json
{
  "attack_type": "directory_brute_force",
  "endpoint": "/admin.php",
  "ip_address": "192.168.1.100",
  "payload": "40 404 errors in 5 minutes",
  "severity": "medium",
  "blocked": false,
  "details": "Directory brute force detected: 40 failed requests",
  "risk_score": 55,
  "classification": "reconnaissance_reconnaissance",
  "recommended_action": "alert_admin"
}
```

### 7. Suspicious User Agent

**Detection:**
```python
# In security middleware
user_agent = request.headers.get('User-Agent', '').lower()
if 'sqlmap' in user_agent or 'nikto' in user_agent:
    log_attack(
        attack_type='suspicious_activity',
        endpoint=request.path,
        payload=f'User-Agent: {user_agent}',
        severity='medium',
        blocked=False
    )
```

**Example Tools Detected:**
- sqlmap
- nikto
- nmap
- burp
- metasploit
- dirbuster
- gobuster
- ffuf

**Logged Information:**
```json
{
  "attack_type": "suspicious_activity",
  "endpoint": "/valves",
  "ip_address": "192.168.1.100",
  "user_agent": "sqlmap/1.0",
  "payload": "User-Agent: sqlmap",
  "severity": "medium",
  "blocked": false,
  "details": "Suspicious user agent detected: sqlmap",
  "risk_score": 50,
  "classification": "reconnaissance_reconnaissance",
  "recommended_action": "log_only"
}
```

---

## Complete Flow Diagrams

### Flow 1: SQL Injection Attack

```
User submits search: ' OR 1=1--
         │
         ▼
POST /valves/search
         │
         ▼
Security Middleware
  ├─ Check IP blocked? NO
  ├─ Check user locked? NO
  └─ Check suspicious agent? NO
         │
         ▼
Route Handler (valves.py)
  ├─ Get search term: ' OR 1=1--
  │
  ├─ Call: check_and_log_sql_injection()
  │   │
  │   ├─ detect_sql_injection() → TRUE (matches pattern)
  │   │
  │   └─ log_attack()
  │       ├─ Calculate risk_score: 85
  │       ├─ Classify: exploitation_exploitation
  │       ├─ Recommend: block_ip_permanent
  │       ├─ Store in attack_logs table
  │       │
  │       └─ check_and_execute_auto_response()
  │           ├─ Get rule: "Auto-block SQL injection"
  │           ├─ Check threshold: 3 in 60 min
  │           ├─ Current count: 3
  │           ├─ Trigger? YES
  │           │
  │           └─ execute_block_ip()
  │               ├─ Add to blocked_ips (24h)
  │               ├─ Create SecurityAction log
  │               └─ Update AttackLog: action_taken = "ip_blocked_auto_24h"
  │
  └─ Flash: "Invalid search query detected"
         │
         ▼
Redirect to /valves
         │
         ▼
Next Request from Same IP
         │
         ▼
Security Middleware
  └─ check_ip_blocked() → TRUE
         │
         ▼
Return 403: "Your IP has been blocked"
```

### Flow 2: Failed Login → Account Lock

```
User tries login: admin / wrongpass
         │
         ▼
POST /login
         │
         ▼
Security Middleware (pass)
         │
         ▼
Route Handler (auth.py)
  ├─ Check IP rate limit (10/10min) → OK
  ├─ Check username rate limit (5/15min) → OK
  │
  ├─ User.authenticate() → FAILED
  │
  ├─ log_attack(attack_type='login_brute_force')
  │   └─ Creates attack_logs entry #1
  │
  ├─ FailedLoginTracker.create()
  │   └─ Records failed attempt
  │
  └─ Flash: "Invalid username or password"

[User tries again 4 more times...]

Attempt #5:
POST /login
         │
         ▼
Route Handler (auth.py)
  ├─ Check username rate limit
  │   └─ get_recent_by_username('admin', 15)
  │       └─ Count: 5 attempts
  │
  ├─ Count >= 5? YES
  │
  ├─ Flash: "Account temporarily locked"
  │
  └─ Return 403

Same Time:
Auto-Response System
  ├─ Rule: "Auto-lock after 5 failed logins"
  ├─ Trigger condition: failed_login_per_user
  ├─ Threshold: 5 in 15 minutes
  │
  └─ execute_lock_account()
      ├─ Add to users_locked (2h)
      ├─ Create SecurityAction log
      └─ Update AttackLog: action_taken = "account_locked_auto_2h"

Next Login Attempt:
POST /login
         │
         ▼
Route Handler
  ├─ User.authenticate() → SUCCESS
  ├─ UserLocked.is_locked(user_id) → TRUE
  │
  └─ Flash: "Your account is locked: Auto-locked: login_brute_force"
      Return 403
```

### Flow 3: Admin Views and Responds to Attack

```
Admin logs in
         │
         ▼
Navigate to /monitoring
         │
         ▼
Monitoring Dashboard Loads:
  ├─ AttackLog.get_statistics()
  │   └─ Returns: total, by_type, by_severity
  │
  ├─ AttackLog.get_all(50)
  │   └─ Recent 50 attacks
  │
  ├─ AttackLog.get_high_risk(70, 20)
  │   └─ High-risk attacks (score >= 70)
  │
  ├─ AttackLog.get_actionable(20)
  │   └─ Attacks needing manual action
  │
  ├─ BlockedIP.get_all_active()
  │   └─ Currently blocked IPs
  │
  ├─ UserLocked.get_all_locked()
  │   └─ Currently locked accounts
  │
  ├─ SecurityAction.get_all(20)
  │   └─ Recent security actions
  │
  └─ AutoResponseRule.get_all()
      └─ Auto-response rules status

Admin sees:
┌─────────────────────────────────────┐
│ Attack #456 - SQL Injection         │
│ IP: 192.168.1.100                   │
│ Risk Score: 85                      │
│ Recommended: block_ip_permanent     │
│ Action Taken: ip_blocked_auto_24h   │
│ [View Details] [Unblock IP]         │
└─────────────────────────────────────┘

Admin clicks "View Details":
GET /api/security/attack-details/456
         │
         ▼
Returns:
  ├─ Full attack details
  ├─ Raw request data (JSON)
  └─ Related attacks (attack chain)

Admin clicks "Unblock IP":
POST /api/security/unblock-ip
Body: {"ip_address": "192.168.1.100"}
         │
         ▼
Security Actions Handler
  ├─ BlockedIP.unblock('192.168.1.100')
  ├─ SecurityAction.create(
  │     action_type='unblock_ip',
  │     executed_by=admin_id,
  │     automated=False
  │   )
  └─ Return success

IP is now unblocked, can access system again
```

---

## Summary

The attack logging system provides:

1. **Comprehensive Detection:** 17 attack types with pattern matching and behavioral analysis
2. **Rich Logging:** 20+ fields per attack including context, forensics, and recommendations
3. **Automated Response:** 5 default rules that automatically block, lock, and alert
4. **Admin Visibility:** Dashboard with statistics, filtering, and drill-down capabilities
5. **Reversibility:** All actions can be undone with full audit trails
6. **Attack Chains:** Link multi-stage attacks for investigation
7. **Risk Scoring:** 0-100 score based on attack type, history, and target
8. **Actionable Intelligence:** Specific recommendations with reversal steps

Every attack is:
- **Detected** using patterns or behavior
- **Scored** based on risk factors
- **Classified** into attack stages
- **Logged** with full context
- **Responded to** automatically or manually
- **Visible** in admin dashboard
- **Reversible** if needed
