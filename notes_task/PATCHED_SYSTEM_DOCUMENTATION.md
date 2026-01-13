# Industrial Valve Control System - Patched Version Documentation

## Table of Contents
1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [Database Schema](#database-schema)
4. [Application Components](#application-components)
5. [Security Features](#security-features)
6. [Vulnerability Fixes](#vulnerability-fixes)
7. [Request Flow](#request-flow)
8. [Function Reference](#function-reference)

---

## System Overview

### Purpose
This is a web-based Industrial Control System (ICS) for managing industrial valves in critical infrastructure. The system allows operators and administrators to:
- Monitor valve status in real-time
- Control valve operations (open/close/adjust)
- Schedule automated valve operations
- Upload firmware and configuration files
- View command logs and attack attempts
- Manage security incidents

### Technology Stack
- **Backend**: Flask (Python web framework)
- **Database**: SQLite3
- **Authentication**: Werkzeug password hashing
- **Encryption**: PyCryptodome (AES-256-CBC)
- **File Type Detection**: python-magic

### User Roles
1. **Admin**: Full system access, including security monitoring and file uploads
2. **Operator**: Can control valves and view logs, limited administrative access

---

## Architecture

### Directory Structure
```
patched/
├── app/
│   ├── app.py                    # Main Flask application
│   ├── models.py                 # Database models and ORM
│   ├── routes/                   # Route blueprints
│   │   ├── auth.py              # Authentication routes
│   │   ├── dashboard.py         # Dashboard routes
│   │   ├── valves.py            # Valve control routes
│   │   ├── upload.py            # File upload routes
│   │   ├── monitoring.py        # Security monitoring routes
│   │   ├── logs.py              # Log viewing routes
│   │   └── security_actions.py  # Security response routes
│   ├── utils/                    # Utility modules
│   │   ├── auth_helpers.py      # Authentication decorators
│   │   ├── monitoring.py        # Attack detection system
│   │   ├── auto_response.py     # Automated security responses
│   │   └── security_middleware.py # Request security checks
│   ├── static/                   # CSS, JavaScript
│   └── templates/                # HTML templates
├── database/
│   └── valves.db                # SQLite database
├── uploads/                      # File upload directory
├── init_db.py                   # Database initialization
├── populate_db.py               # Sample data generation
└── run.py                       # Application entry point
```

### Application Flow
1. **Request arrives** → Security middleware checks
2. **Authentication** → Session validation
3. **Authorization** → Role-based access control
4. **Route handler** → Business logic execution
5. **Security monitoring** → Attack detection and logging
6. **Response** → Data returned to client

---

## Database Schema

### Core Tables

#### 1. users
Stores user account information.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Unique user identifier |
| username | TEXT UNIQUE | Login username |
| password_hash | TEXT | Bcrypt hashed password |
| role | TEXT | 'admin' or 'operator' |
| email | TEXT | User email address |
| created_at | TIMESTAMP | Account creation time |
| last_login | TIMESTAMP | Last successful login |

**Purpose**: User authentication and authorization.

#### 2. valves
Represents physical industrial valves.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Unique valve identifier |
| valve_name | TEXT UNIQUE | Human-readable valve name |
| location | TEXT | Physical location |
| open_percentage | INTEGER | Current opening (0-100%) |
| status | TEXT | operational/maintenance/error/offline |
| communication_status | TEXT | connected/disconnected/timeout |
| last_command | TEXT | Last command sent |
| last_command_timestamp | TIMESTAMP | When command was sent |
| last_response_timestamp | TIMESTAMP | When response received |
| firmware_version | TEXT | Current firmware version |
| config_file | TEXT | Associated config file |
| created_at | TIMESTAMP | Valve registration time |
| updated_at | TIMESTAMP | Last status update |

**Purpose**: Track valve state and operational status.

#### 3. command_logs
Logs all commands sent to valves.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Log entry identifier |
| valve_id | INTEGER FK | Target valve |
| command | TEXT | Command sent (OPEN/CLOSE/ADJUST/SYNC) |
| user_id | INTEGER FK | User who executed command |
| target_percentage | INTEGER | Desired valve position |
| status | TEXT | success/failed/timeout |
| response_time_ms | INTEGER | Command response time |
| error_message | TEXT | Error details if failed |
| timestamp | TIMESTAMP | When command was executed |

**Purpose**: Audit trail of all valve operations.

#### 4. schedules
Scheduled valve operations.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Schedule identifier |
| valve_id | INTEGER FK | Target valve |
| scheduled_time | TIMESTAMP | When to execute |
| command | TEXT | Command to execute |
| target_percentage | INTEGER | Desired valve position |
| created_by | INTEGER FK | User who created schedule |
| status | TEXT | pending/executed/cancelled/failed |
| executed_at | TIMESTAMP | Actual execution time |
| created_at | TIMESTAMP | Schedule creation time |

**Purpose**: Automate valve operations at specific times.

#### 5. file_uploads
Tracks uploaded firmware and configuration files.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Upload identifier |
| original_filename | TEXT | Original file name |
| stored_filename | TEXT | System-generated filename |
| file_type | TEXT | firmware/config/encrypted |
| file_size | INTEGER | File size in bytes |
| upload_endpoint | TEXT | Which endpoint was used |
| uploaded_by | INTEGER FK | User who uploaded |
| is_encrypted | BOOLEAN | Whether file is encrypted |
| scan_status | TEXT | pending/clean/malicious/skipped |
| applied_to_valve | INTEGER FK | Which valve it's for |
| upload_timestamp | TIMESTAMP | Upload time |

**Purpose**: Track and audit file uploads for security.

### Security Tables

#### 6. attack_logs
Comprehensive attack detection logs.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Log identifier |
| attack_type | TEXT | Type of attack detected |
| endpoint | TEXT | Targeted URL |
| user_id | INTEGER FK | Authenticated user (if any) |
| ip_address | TEXT | Source IP address |
| user_agent | TEXT | Browser/tool user agent |
| request_method | TEXT | HTTP method (GET/POST) |
| payload | TEXT | Attack payload |
| severity | TEXT | low/medium/high/critical |
| blocked | BOOLEAN | Whether attack was blocked |
| details | TEXT | Additional attack details |
| classification | TEXT | Attack category |
| recommended_action | TEXT | Suggested response |
| action_taken | TEXT | What was done |
| action_reversible | BOOLEAN | Can action be undone |
| reverse_action_steps | TEXT | How to reverse (JSON) |
| risk_score | INTEGER | Risk level (0-100) |
| related_attack_id | INTEGER FK | Linked attack in chain |
| raw_request_data | TEXT | Full request details (JSON) |
| response_status | INTEGER | HTTP response code |
| geolocation | TEXT | Geographic location |
| timestamp | TIMESTAMP | Detection time |

**Purpose**: Central security logging and incident tracking.

**Attack Types**:
- `sql_injection`: SQL injection attempts
- `file_upload_abuse`: Malicious file uploads
- `size_bypass`: File size limit bypass attempts
- `mime_bypass`: MIME type filtering bypass
- `encrypted_payload`: Encrypted malicious content
- `suspicious_activity`: Scanning tools detected
- `login_brute_force`: Password guessing
- `directory_brute_force`: Directory enumeration
- `session_hijacking`: Session manipulation
- `cookie_manipulation`: Cookie tampering
- `rate_limit_violation`: Too many requests
- `privilege_escalation`: Unauthorized access attempts
- `path_traversal`: Directory traversal attempts
- `csrf_attempt`: Cross-site request forgery
- `xss_attempt`: Cross-site scripting
- `unauthorized_access`: Access to restricted resources

#### 7. blocked_ips
Blacklisted IP addresses.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Block entry identifier |
| ip_address | TEXT UNIQUE | Blocked IP address |
| reason | TEXT | Why it was blocked |
| blocked_at | TIMESTAMP | When blocked |
| blocked_until | TIMESTAMP | When to auto-unblock (NULL = permanent) |
| auto_unblock | BOOLEAN | Whether to unblock automatically |
| blocked_by_user_id | INTEGER FK | Admin who blocked (if manual) |
| attack_log_id | INTEGER FK | Related attack |
| is_active | BOOLEAN | Currently enforced |

**Purpose**: Block malicious IP addresses from accessing system.

#### 8. failed_login_attempts
Tracks failed authentication attempts.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Attempt identifier |
| username | TEXT | Attempted username |
| ip_address | TEXT | Source IP |
| attempt_time | TIMESTAMP | When attempt occurred |
| user_agent | TEXT | Browser/tool user agent |
| attack_log_id | INTEGER FK | Related attack log |

**Purpose**: Detect brute force attacks and credential stuffing.

#### 9. security_actions
Log of security responses taken.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Action identifier |
| action_type | TEXT | Type of action taken |
| target | TEXT | What was acted upon |
| reason | TEXT | Why action was taken |
| executed_at | TIMESTAMP | When executed |
| executed_by | INTEGER FK | Admin who executed |
| reversed_at | TIMESTAMP | When reversed (if applicable) |
| reversed_by | INTEGER FK | Admin who reversed |
| attack_log_id | INTEGER FK | Related attack |
| automated | BOOLEAN | Whether automatic |

**Purpose**: Audit trail of security responses.

**Action Types**:
- `block_ip`: Block IP address
- `unblock_ip`: Unblock IP address
- `lock_account`: Lock user account
- `unlock_account`: Unlock user account
- `clear_sessions`: Terminate user sessions
- `delete_file`: Remove uploaded file
- `quarantine_file`: Isolate suspicious file
- `alert_admin`: Notify administrator

#### 10. auto_response_rules
Automated security response configuration.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Rule identifier |
| rule_name | TEXT UNIQUE | Rule name |
| attack_type | TEXT | Which attack type triggers |
| trigger_condition | TEXT | When to trigger |
| action_type | TEXT | What action to take |
| threshold | INTEGER | Trigger threshold |
| time_window_minutes | INTEGER | Time window for counting |
| enabled | BOOLEAN | Whether rule is active |
| created_at | TIMESTAMP | Rule creation time |
| updated_at | TIMESTAMP | Last modification |

**Purpose**: Configure automatic incident response.

**Default Rules**:
1. Auto-block after 5 failed logins in 10 minutes
2. Auto-block after 3 SQL injection attempts in 60 minutes
3. Auto-lock account after 5 failed login attempts in 15 minutes
4. Rate limit after 100 requests per minute
5. Block privilege escalation attempts immediately

#### 11. users_locked
Locked user accounts.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Lock entry identifier |
| user_id | INTEGER UNIQUE FK | Locked user |
| locked_at | TIMESTAMP | When locked |
| locked_until | TIMESTAMP | When to auto-unlock (NULL = manual) |
| reason | TEXT | Why locked |
| locked_by | INTEGER FK | Admin who locked |
| security_action_id | INTEGER FK | Related security action |

**Purpose**: Temporarily or permanently disable user accounts.

---

## Application Components

### 1. app.py (Main Application)

**Purpose**: Bootstrap the Flask application and register all components.

**Key Functions**:

```python
app = Flask(__name__)
app.secret_key = os.urandom(24)  # Random session key for security
app.config['SESSION_TYPE'] = 'filesystem'
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB max upload
```

**Security Middleware Registration**:
```python
@app.before_request
def before_request_security():
    return security_checks()  # Runs before every request
```

**Blueprints Registered**:
1. `auth_bp`: Authentication (login/logout)
2. `dashboard_bp`: Main dashboard
3. `valves_bp`: Valve control
4. `upload_bp`: File uploads
5. `monitoring_bp`: Security monitoring
6. `logs_bp`: Command logs
7. `security_actions_bp`: Security responses

---

### 2. models.py (Database Models)

All database interactions use parameterized queries to prevent SQL injection.

#### User Model

**User.create(username, password, role, email)**
- Creates new user with hashed password
- Uses `werkzeug.security.generate_password_hash()`
- Returns: user_id

**User.authenticate(username, password)**
- Validates credentials using parameterized query
- Compares hash with `check_password_hash()`
- Returns: User dict or None

**User.get_by_id(user_id)**
- Retrieves user by ID (excludes password_hash)
- Returns: User dict or None

**User.update_last_login(user_id)**
- Updates last_login timestamp
- Called on successful authentication

#### Valve Model

**Valve.get_all()**
- Returns: List of all valves

**Valve.get_by_id(valve_id)**
- Returns: Single valve dict or None

**Valve.search(search_term)**
- **SECURE**: Uses parameterized queries with LIKE
- Returns: Filtered valve list

**Valve.update_status(valve_id, open_percentage, command, user_id)**
- Updates valve state after command execution
- Records timestamps

**Valve.update_communication_status(valve_id, status)**
- Updates connection status

#### CommandLog Model

**CommandLog.create(...)**
- Logs every valve command
- Records success/failure, response time, errors

**CommandLog.get_by_valve(valve_id, limit)**
- Returns: Command history for specific valve

**CommandLog.get_all(limit)**
- Returns: Recent commands across all valves

**CommandLog.get_failed(limit)**
- Returns: Failed commands only

**CommandLog.get_timeouts(limit)**
- Returns: Timed-out commands only

#### Schedule Model

**Schedule.create(...)**
- Creates scheduled valve operation
- Validates datetime format

**Schedule.get_all()**
- Returns: All schedules with valve and user details

**Schedule.get_pending()**
- Returns: Schedules awaiting execution

**Schedule.cancel(schedule_id)**
- Marks schedule as cancelled

#### FileUpload Model

**FileUpload.create(...)**
- Records file upload metadata
- Tracks encryption status and scan results

**FileUpload.get_all()**
- Returns: All uploaded files with uploader details

#### Security Models

**BlockedIP.create(...)**
- Adds IP to blocklist
- Supports temporary and permanent blocks

**BlockedIP.is_blocked(ip_address)**
- Checks if IP is currently blocked
- Considers expiration times

**BlockedIP.unblock(ip_address)**
- Removes IP from blocklist

**BlockedIP.get_all_active()**
- Returns: Currently blocked IPs

**BlockedIP.cleanup_expired()**
- Automatically removes expired blocks

**FailedLoginTracker.create(...)**
- Records failed login attempt

**FailedLoginTracker.get_recent_by_username(username, minutes)**
- Returns: Recent failures for username

**FailedLoginTracker.get_recent_by_ip(ip_address, minutes)**
- Returns: Recent failures from IP

**SecurityAction.create(...)**
- Logs security action taken
- Marks as automated or manual

**SecurityAction.reverse_action(action_id, reversed_by)**
- Marks action as reversed
- Tracks who reversed it

**AutoResponseRule.get_by_attack_type(attack_type)**
- Returns: Enabled rules for attack type

**AutoResponseRule.toggle_enabled(rule_id)**
- Enable/disable rule

**UserLocked.lock_user(...)**
- Locks user account
- Supports temporary and permanent locks

**UserLocked.is_locked(user_id)**
- Checks if user is currently locked

**UserLocked.unlock_user(user_id)**
- Unlocks user account

**AttackLog.create(...)**
- Creates comprehensive attack log
- Calculates risk score and classification

**AttackLog.get_all(limit)**
- Returns: Recent attacks

**AttackLog.get_by_ip(ip_address, limit)**
- Returns: Attacks from specific IP

**AttackLog.get_recent_by_ip(ip_address, minutes)**
- Returns: Recent attacks from IP (for rate calculation)

**AttackLog.get_high_risk(threshold, limit)**
- Returns: High-risk attacks

**AttackLog.get_actionable(limit)**
- Returns: Attacks requiring admin action

**AttackLog.get_attack_chains(attack_id)**
- Returns: Related attacks (multi-stage)

**AttackLog.mark_action_taken(attack_id, action_taken)**
- Records response action

**AttackLog.get_statistics()**
- Returns: Aggregated attack statistics

---

### 3. Routes

#### auth.py (Authentication Routes)

**GET/POST /login**
- **Function**: Authenticate users and create sessions
- **Security Features**:
  - Rate limiting: Max 10 failed attempts per IP in 10 minutes
  - Account lockout: Max 5 failed attempts per user in 15 minutes
  - Failed login tracking
  - Attack logging
  - User account lock checking
- **Process**:
  1. Check IP rate limit (10 attempts/10min)
  2. Check username rate limit (5 attempts/15min)
  3. Authenticate credentials using parameterized query
  4. Check if user account is locked
  5. Create session on success
  6. Log failed attempt on failure
  7. Display warning if previous failed attempts exist
- **Vulnerabilities Fixed**: Brute force prevention

**GET /logout**
- Clears session
- Redirects to login

#### dashboard.py (Dashboard Routes)

**GET /dashboard**
- **Decorator**: @login_required
- **Function**: Display system overview
- **Data Displayed**:
  - Total valves count
  - Operational valves count
  - Connected valves count
  - Average valve opening percentage
  - Recent 10 command logs
  - Pending schedules (max 5)
  - Top 20 valves by name

#### valves.py (Valve Control Routes)

**GET /valves**
- **Decorator**: @login_required
- **Function**: List all valves

**GET /valve/<valve_id>**
- **Decorator**: @login_required
- **Function**: View valve details and recent logs
- **Shows**: 20 most recent commands for valve

**POST /valves/search**
- **Decorator**: @login_required
- **Function**: Search valves by name or location
- **Security Feature**: SQL injection detection
- **PATCHED**: Always uses parameterized queries
- **Process**:
  1. Get search term from form
  2. Check for SQL injection patterns
  3. Block request if attack detected
  4. Use Valve.search() with parameterized query
  5. Return filtered results
- **Vulnerability Fixed**: SQL injection completely prevented

**POST /valve/<valve_id>/control**
- **Decorator**: @operator_or_admin_required
- **Function**: Execute valve command
- **Commands**:
  - `open`: Set to 100%
  - `close`: Set to 0%
  - `adjust`: Set to specific percentage
  - `sync`: Resync current state
- **Validation**:
  - Percentage must be 0-100
  - Valve must exist
- **Simulation**:
  - 90% success rate
  - Random response time (50-500ms success, 1000-5000ms failure)
  - Random error messages on failure
- **Logging**: Every command logged to command_logs

**GET /schedules**
- **Decorator**: @login_required
- **Function**: View all scheduled operations

**POST /schedules/create**
- **Decorator**: @operator_or_admin_required
- **Function**: Create scheduled valve operation
- **Validation**:
  - Valve ID required
  - Datetime format validation
  - Command validation
  - Percentage validation for ADJUST

**POST /schedules/<schedule_id>/cancel**
- **Decorator**: @operator_or_admin_required
- **Function**: Cancel scheduled operation

#### upload.py (File Upload Routes)

**GET /upload**
- **Decorator**: @admin_required
- **Function**: Display upload interface and file history

**POST /upload/secure**
- **Decorator**: @admin_required
- **Function**: Secure file upload endpoint (PATCHED)
- **Security Features**:
  1. **Filename Sanitization**: Uses `secure_filename()` from werkzeug
  2. **Extension Whitelist**: Only .bin and .conf allowed
  3. **Size Limit**: 5MB maximum
  4. **Content-Type Validation**: Uses python-magic to verify actual file type
  5. **Random Filename**: Uses secrets.token_hex(16) for storage
  6. **Separate Directories**: firmware/ and configs/
- **Process**:
  1. Check file provided
  2. Sanitize filename
  3. Validate extension against whitelist
  4. Check file size
  5. Generate random storage filename
  6. Save to appropriate directory
  7. Validate content using magic bytes
  8. Remove file if validation fails
  9. Record upload in database
- **Vulnerabilities Fixed**: 
  - Path traversal prevented by secure_filename
  - Malicious extensions blocked by whitelist
  - Size bypass prevented by actual size check
  - Content type spoofing prevented by magic validation

**POST /upload/encrypted**
- **Decorator**: @admin_required
- **Function**: Upload encrypted files
- **Encryption**: AES-256-CBC with fixed key (demonstration purposes)
- **Process**:
  1. Read file content
  2. Validate extension (.bin or .conf)
  3. Check file size
  4. Encrypt using AES-CBC
  5. Prepend IV to encrypted content
  6. Save with .enc extension
  7. Record in database
- **Security Note**: Validation happens before encryption in patched version

**POST /upload/encrypted/decrypt/<file_id>**
- **Decorator**: @admin_required
- **Function**: Decrypt and validate encrypted file
- **SECURITY CRITICAL - Decrypt-Then-Scan Pipeline**:
  1. Retrieve encrypted file metadata
  2. Read IV and encrypted content
  3. Decrypt using AES-CBC
  4. **SCAN AFTER DECRYPTION** ← KEY FIX
  5. Check for malicious patterns (<?php, <script, etc.)
  6. Validate MIME type on decrypted content
  7. Verify size limits on decrypted content
  8. Only save if all checks pass
- **Vulnerability Fixed**: Scan-then-decrypt bypass eliminated

#### monitoring.py (Security Monitoring Routes)

**GET /monitoring**
- **Decorator**: @admin_required
- **Function**: Security dashboard
- **Displays**:
  - Attack statistics
  - Recent 50 attacks
  - High-risk attacks (score ≥ 70)
  - Actionable attacks (requiring response)
  - Blocked IPs
  - Locked accounts
  - Recent 20 security actions
  - Auto-response rules

**GET /api/monitoring/stats**
- **Decorator**: @admin_required
- **Returns**: JSON attack statistics

**GET /api/monitoring/attacks**
- **Decorator**: @admin_required
- **Parameters**: limit, type, risk_threshold
- **Returns**: Filtered attack logs

**GET /api/monitoring/actionable**
- **Decorator**: @admin_required
- **Returns**: Attacks requiring manual action

#### logs.py (Log Viewing Routes)

**GET /logs/commands**
- **Decorator**: @login_required
- **Function**: View all command logs
- **Parameter**: limit (default 100)

**GET /logs/failures**
- **Decorator**: @login_required
- **Function**: View failed commands only

**GET /logs/timeouts**
- **Decorator**: @login_required
- **Function**: View timed-out commands only

#### security_actions.py (Security Response Routes)

**POST /api/security/block-ip**
- **Decorator**: @admin_required
- **Function**: Manually block IP address
- **Parameters**: ip_address, reason, duration_hours
- **Creates**: BlockedIP entry and SecurityAction log

**POST /api/security/unblock-ip**
- **Decorator**: @admin_required
- **Function**: Remove IP from blocklist

**POST /api/security/lock-account**
- **Decorator**: @admin_required
- **Function**: Lock user account
- **Parameters**: user_id, reason, duration_hours

**POST /api/security/unlock-account**
- **Decorator**: @admin_required
- **Function**: Unlock user account

**POST /api/security/clear-sessions**
- **Decorator**: @admin_required
- **Function**: Terminate user sessions (logged only)

**GET /api/security/blocked-ips**
- **Decorator**: @admin_required
- **Returns**: Active blocked IPs

**GET /api/security/actions-history**
- **Decorator**: @admin_required
- **Returns**: Security action history

**POST /api/security/reverse-action/<action_id>**
- **Decorator**: @admin_required
- **Function**: Reverse security action
- **Supports**: Unblocking IPs, unlocking accounts

**POST /api/security/configure-auto-response**
- **Decorator**: @admin_required
- **Function**: Configure auto-response rules
- **Actions**: toggle, update_threshold

**GET /api/security/auto-response-rules**
- **Decorator**: @admin_required
- **Returns**: All auto-response rules

**GET /api/security/attack-details/<attack_id>**
- **Decorator**: @admin_required
- **Returns**: Attack details and related attack chain

**GET /api/security/locked-accounts**
- **Decorator**: @admin_required
- **Returns**: Currently locked accounts

---

### 4. Utility Modules

#### auth_helpers.py (Authorization Decorators)

**@login_required**
- Checks if 'user_id' exists in session
- Redirects to login if not authenticated
- Flash message: "Please log in to access this page"

**@admin_required**
- Requires authentication
- Checks if role is 'admin'
- Redirects to dashboard if insufficient privileges
- Flash message: "Admin access required"

**@operator_or_admin_required**
- Requires authentication
- Checks if role is 'admin' or 'operator'
- Redirects to dashboard if insufficient privileges
- Flash message: "Operator or Admin access required"

#### monitoring.py (Attack Detection System)

**Detection Patterns**:

```python
SQL_INJECTION_PATTERNS = [
    r"(\bUNION\b.*\bSELECT\b)",  # UNION SELECT
    r"(\bOR\b\s+\d+\s*=\s*\d+)",  # OR 1=1
    r"('|\")(\s*OR\s*\1\s*=\s*\1)",  # ' OR '='
    r"(;|\-\-|\/\*|\*\/)",  # Comment markers
    r"(\bDROP\b|\bDELETE\b|\bINSERT\b|\bUPDATE\b)",  # DML
    r"('.*--)",  # String with comment
    r"('\s*;\s*--)",  # Semicolon comment
]

XSS_PATTERNS = [
    r'<script[^>]*>',
    r'javascript:',
    r'onerror\s*=',
    r'onload\s*=',
    r'<iframe[^>]*>',
    r'eval\(',
    r'expression\(',
]

PATH_TRAVERSAL_PATTERNS = [
    r'\.\.[/\\]',  # ../
    r'\.\.%2[fF]',  # ..%2F
    r'%2e%2e[/\\]',  # %2e%2e/
    r'\.\.\\',  # ..\
]

SUSPICIOUS_EXTENSIONS = [
    '.php', '.php3', '.php4', '.php5', '.phtml',
    '.py', '.sh', '.bat', '.exe', '.cmd',
    '.jsp', '.asp', '.aspx', '.rb', '.pl'
]

SUSPICIOUS_USER_AGENTS = [
    'nikto', 'sqlmap', 'nmap', 'masscan', 'burp', 
    'metasploit', 'havij', 'acunetix', 'wpscan', 
    'dirbuster', 'gobuster', 'ffuf'
]
```

**Key Functions**:

**calculate_risk_score(attack_type, ip_address, user_id, endpoint)**
- Base scores by attack type (40-90)
- Increases by 5 per recent attack from same IP
- Adds 10 for admin endpoint targeting
- Returns: 0-100 risk score

**classify_attack(attack_type, endpoint, payload)**
- Categories: reconnaissance, exploitation, post_exploitation
- Stages: Same categories
- Used for attack chain analysis

**recommend_action(attack_type, risk_score, attack_count)**
- SQL injection → block_ip_permanent
- Login brute force (5+) → block_ip_temporary
- Privilege escalation → block_ip_and_alert
- Rate limit (risk>60) → rate_limit
- Risk≥80 → block_ip_and_alert
- Risk≥60 → alert_admin
- Default → log_only

**detect_sql_injection(input_string)**
- Tests against all SQL_INJECTION_PATTERNS
- Returns: True if pattern matches

**detect_xss(input_string)**
- Tests against XSS_PATTERNS
- Returns: True if pattern matches

**detect_path_traversal(input_string)**
- Tests against PATH_TRAVERSAL_PATTERNS
- Returns: True if pattern matches

**detect_file_upload_abuse(filename, content_type, file_size)**
- Checks for suspicious extensions
- Detects path traversal in filename
- Identifies double extensions
- Validates file size
- Returns: List of issues

**detect_suspicious_user_agent()**
- Checks User-Agent header against known tools
- Returns: (is_suspicious, tool_name)

**detect_directory_brute_force(ip_address)**
- Tracks 404 errors per IP
- Threshold: 20 in 5 minutes
- Returns: (is_brute_force, count)

**detect_rate_limit_violation(ip_address, endpoint)**
- Tracks requests per IP per endpoint
- Threshold: 100 per minute
- Returns: (is_violation, count)

**detect_session_anomaly(user_id, ip_address)**
- Checks if session IP changed
- Detects session hijacking
- Returns: (is_anomaly, details)

**detect_cookie_manipulation()**
- Checks for oversized cookies (>1000 bytes)
- Checks for suspicious characters (<, >, ", ')
- Returns: (is_manipulated, details)

**detect_privilege_escalation(user_role, endpoint)**
- Checks if operator accessing admin endpoints
- Admin endpoints: /admin, /monitoring, /api/security, /upload
- Returns: (is_escalation, details)

**log_attack(...)**
- Central logging function
- Calculates risk score if not provided
- Classifies attack if not provided
- Recommends action if not provided
- Stores full request details as JSON
- Triggers auto-response system
- Returns: attack_id

**check_and_log_[attack_type](...)**
- Convenience wrappers for specific attack types
- Each calls respective detection function
- Logs if attack detected
- Returns: True if attack detected

#### auto_response.py (Automated Security Responses)

**check_and_execute_auto_response(attack_id, attack_type, ip_address, user_id, risk_score)**
- Main entry point called after attack logging
- Gets all enabled rules for attack type
- Evaluates each rule's trigger condition
- Executes action if triggered

**should_trigger_rule(rule, attack_type, ip_address, user_id, risk_score)**
- Evaluates trigger conditions:
  - `failed_attempts`: Count failed logins by IP
  - `failed_login_per_user`: Count failed logins by username
  - `attack_count`: Count specific attack type from IP
  - `requests_per_minute`: Count recent requests from IP
  - `risk_score`: Compare calculated risk score
- Returns: True if threshold exceeded

**execute_action(action_type, rule, attack_id, ip_address, user_id, attack_type_name)**
- Dispatches to specific action handler
- Actions: block_ip, lock_account, alert_admin, rate_limit

**execute_block_ip(ip_address, rule, attack_id, attack_type_name)**
- Creates BlockedIP entry (24 hour auto-unblock)
- Creates SecurityAction log (automated=True)
- Updates attack log with action taken

**execute_lock_account(user_id, rule, attack_id, attack_type_name)**
- Creates UserLocked entry (2 hour auto-unlock)
- Creates SecurityAction log
- Updates attack log

**execute_alert_admin(ip_address, user_id, rule, attack_id, attack_type_name)**
- Creates SecurityAction log (type: alert_admin)
- Updates attack log
- (In production, would send email/SMS)

**execute_rate_limit(ip_address, rule, attack_id, attack_type_name)**
- Creates temporary block (30 minutes)
- Creates SecurityAction log
- Updates attack log

**cleanup_expired_blocks()**
- Removes expired auto-unblock entries
- Should be called periodically (cron job)

**cleanup_old_logs()**
- Removes failed login attempts older than 7 days
- Keeps database size manageable

#### security_middleware.py (Request Security Checks)

**check_ip_blocked()**
- Checks if request IP is in blocked_ips
- Returns 403 JSON error if blocked
- Includes reason and contact info

**check_user_locked()**
- Checks if authenticated user is locked
- Clears session if locked
- Returns 403 JSON error if locked
- Includes reason and lock duration

**track_ip_in_session()**
- Stores IP address in session on login
- Used for session hijacking detection

**security_checks()**
- **Called before every request** via @app.before_request
- Runs all security checks in order:
  1. Check IP blocklist
  2. Check user lock status
  3. Track session IP
  4. Check for suspicious user agents
  5. Check for cookie manipulation (non-static paths)
- Returns error response if check fails, None if all pass

**rate_limit_check(endpoint_prefix)**
- Optional additional rate limiting for specific endpoints
- Returns 429 if limit exceeded

**log_404_handler(error)**
- Called for all 404 errors via @app.errorhandler(404)
- Logs for directory brute force detection
- Returns JSON error response

**require_role(required_role)**
- Decorator factory for role-based access control
- Alternative to auth_helpers decorators
- Logs unauthorized access attempts

---

## Security Features

### 1. Authentication Security

**Password Storage**:
- Werkzeug bcrypt hashing
- Salt automatically included
- Computationally expensive (brute force resistant)

**Session Management**:
- Random 24-byte secret key
- Filesystem-based sessions
- Session cleared on logout
- IP tracking for hijacking detection

**Brute Force Protection**:
- IP-based rate limiting: 10 attempts per 10 minutes
- Username-based rate limiting: 5 attempts per 15 minutes
- Failed attempts logged with timestamp
- Auto-block via auto-response rules
- Account lock after 5 failed attempts

### 2. Authorization

**Role-Based Access Control (RBAC)**:
- Decorators enforce role requirements
- Three levels: guest (none), operator, admin
- Privilege escalation attempts logged
- Unauthorized access returns 403

**Endpoint Protection**:
- All sensitive endpoints require @admin_required
- Valve control requires @operator_or_admin_required
- Viewing requires @login_required minimum

### 3. SQL Injection Prevention

**Complete Mitigation**:
- **All queries use parameterized statements**
- No string concatenation in SQL
- User input never directly embedded
- Works for all user roles (admin included)

**Example (Patched)**:
```python
# SECURE: Parameterized query
valves = conn.execute(
    'SELECT * FROM valves WHERE valve_name LIKE ? OR location LIKE ?',
    (f'%{search_term}%', f'%{search_term}%')
).fetchall()
```

**Attack Detection**:
- Pattern matching on all user input
- SQL keywords: UNION, SELECT, OR, DROP, etc.
- Comment markers: --, /*, */
- Logged even though blocked

### 4. File Upload Security

**Multiple Defense Layers**:

**Layer 1: Filename Sanitization**
- `secure_filename()` removes path traversal
- Prevents: ../../../etc/passwd

**Layer 2: Extension Whitelist**
- Only .bin and .conf allowed
- Blacklist approach insufficient
- Prevents: .php, .jsp, .exe, etc.

**Layer 3: Size Validation**
- Server-side size check (5MB limit)
- Checks actual file size after upload
- Prevents: Size bypass via headers

**Layer 4: Content-Type Validation**
- python-magic checks actual file type
- Uses magic bytes, not headers
- Prevents: MIME type spoofing

**Layer 5: Random Filenames**
- Cryptographically secure random names
- Prevents: Predictable file paths
- Uses: secrets.token_hex(16)

**Layer 6: Separate Directories**
- Firmware in uploads/firmware/
- Configs in uploads/configs/
- Encrypted in uploads/encrypted/
- Prevents: Execution in web root

### 5. Encrypted File Handling

**Encryption-Then-Scan Pipeline (FIXED)**:

**Vulnerable Flow** (old):
```
Upload → Scan → Encrypt → Store
```
Problem: Attacker sees scan results, adjusts payload

**Secure Flow** (patched):
```
Upload → Encrypt → Store → (On Decrypt) → Scan → Decision
```

**Security Benefits**:
1. Attacker cannot iterate based on scan results
2. Malicious content detected after decryption
3. File only saved if all checks pass
4. Content validation on actual data

**Decryption Security Checks**:
1. Verify file exists and is marked encrypted
2. Decrypt using stored IV
3. Scan for malicious patterns:
   - <?php (PHP code)
   - <script> (JavaScript)
   - <iframe> (iframe injection)
   - eval() (code execution)
   - exec() (command execution)
4. Validate MIME type of decrypted content
5. Check size limits on decrypted content
6. Only save if all checks pass

### 6. Attack Detection and Response

**Real-Time Monitoring**:
- All requests analyzed
- Patterns matched against signatures
- Risk score calculated dynamically
- Attack chains tracked via related_attack_id

**Detection Categories**:
1. **Reconnaissance**: Directory brute force, scanning tools
2. **Exploitation**: SQL injection, file upload abuse, XSS
3. **Post-Exploitation**: Privilege escalation, session hijacking

**Automated Response**:
- Rules trigger on thresholds
- Actions: block IP, lock account, rate limit, alert
- Configurable via admin interface
- All actions logged and reversible

**Manual Response**:
- Admin dashboard shows actionable attacks
- One-click block/unblock
- Action reversal supported
- Full audit trail

### 7. Session Security

**Session Hijacking Detection**:
- IP address stored in session on login
- Compared on each request
- Anomaly logged if IP changes
- Session terminated if suspicious

**Cookie Security**:
- Size limit enforced (1000 bytes)
- Special characters detected (<, >, ", ')
- Manipulation logged as attack

### 8. Rate Limiting

**Global Rate Limiting**:
- Tracks requests per IP per endpoint
- Threshold: 100 requests per minute
- Temporary block (30 minutes) on violation
- In-memory tracking (defaultdict)

**Attack-Specific Rate Limiting**:
- Login attempts: 10 per 10 minutes per IP
- Failed logins: 5 per 15 minutes per username
- 404 errors: 20 per 5 minutes (directory brute force)

### 9. Input Validation

**All User Input Validated**:
- Length limits enforced
- Type checking (int, date, enum)
- Pattern matching for attacks
- Sanitization before processing

**Specific Validations**:
- Valve percentage: 0-100 integer
- Datetime: ISO format required
- Command: Must be in allowed list
- File extension: Whitelist only
- Username: Alphanumeric recommended

---

## Vulnerability Fixes

### Fix 1: SQL Injection Prevention

**Vulnerability Location**: `/valves/search` endpoint
- **Vulnerable Code** (vulnerable/app/routes/valves.py:44):
```python
# VULNERABLE: String concatenation
query = f"SELECT * FROM valves WHERE valve_name LIKE '%{search_term}%' OR location LIKE '%{search_term}%'"
valves_raw = conn.execute(query).fetchall()
```

**Attack Payload**:
```
' OR 1=1--
```

**Result**: Returns all valves, bypasses search logic

**Fix** (patched/app/routes/valves.py:79-81):
```python
# FIXED: Parameterized query
valves = conn.execute(
    'SELECT * FROM valves WHERE valve_name LIKE ? OR location LIKE ? ORDER BY valve_name',
    (f'%{search_term}%', f'%{search_term}%')
).fetchall()
```

**Why It Works**:
- Database driver handles escaping
- User input treated as data, never as code
- No string concatenation in SQL
- Works identically for all users

**Additional Protection**:
- SQL injection patterns detected
- Attack logged even though blocked
- Admin notified of attempts

### Fix 2: File Upload Vulnerabilities (Multiple Scenarios)

#### Scenario 1: No Validation (REMOVED in patched)
**Vulnerable Endpoint**: `/upload/scenario1`
- Accepts any filename
- No extension checking
- No content validation
- Stores with original filename

**Attack**: Upload test_malicious.php
**Result**: PHP code executable on server

**Fix**: Endpoint removed, replaced with `/upload/secure`

#### Scenario 2: Bypassable Validation (REMOVED in patched)
**Vulnerable Endpoint**: `/upload/scenario2`
**Vulnerabilities**:
1. Uses header for size check: `X-File-Size` or `Content-Length`
2. Blacklist approach: Only blocks .exe, .sh, .bat, .php
3. Double extension bypass: test.php.bin passes filter

**Attack 1: Size Bypass**
```bash
curl -F "file=@large.bin" -H "X-File-Size: 1000" /upload/scenario2
```
**Result**: 10MB file uploaded despite 5MB limit

**Attack 2: Extension Bypass**
```bash
# Upload malicious.jsp (not in blacklist)
# Or use double extension: malicious.php.bin
```

**Fix**: Endpoint removed, `/upload/secure` enforces:
- Actual file size check after upload
- Whitelist approach (only .bin, .conf)
- Content-type validation with magic bytes
- secure_filename() sanitization

#### Scenario 3: Encrypt-Then-Scan (REMOVED in patched)
**Vulnerable Endpoint**: `/upload/scenario3`
**Vulnerability**: Scans ENCRYPTED content, not actual content
```python
# VULNERABLE: Scanning encrypted file
if not validate_file_content(upload_path):  # Scans .enc file
    os.remove(upload_path)
```

**Attack**: 
1. Create malicious.php
2. Upload via /upload/scenario3 (encrypts it)
3. Scan runs on encrypted bytes (passes)
4. Later decrypt reveals malicious content

**Fix** (patched/app/routes/upload.py:198-230):
```python
# FIXED: Decrypt-Then-Scan pipeline
cipher = AES.new(AES_KEY, AES.MODE_CBC, iv)
decrypted_content = unpad(cipher.decrypt(encrypted_content), AES.block_size)

# Check for malicious patterns in DECRYPTED content
malicious_patterns = [b'<?php', b'<script', b'<iframe', b'eval(', b'exec(']
for pattern in malicious_patterns:
    if pattern in decrypted_content:
        flash('Malicious content detected after decryption - file blocked', 'danger')
        return redirect(url_for('upload.upload_index'))

# Verify file type using magic bytes on DECRYPTED content
if MAGIC_AVAILABLE:
    mime_type = mime.from_buffer(decrypted_content)
    if mime_type not in allowed_mime_types:
        flash(f'Invalid file type after decryption: {mime_type} - file blocked', 'danger')
        return redirect(url_for('upload.upload_index'))
```

**Why It Works**:
- Scans actual content, not encrypted wrapper
- Detects malicious patterns (PHP, JS, etc.)
- Validates MIME type of real content
- File only saved if all checks pass
- Attacker cannot iterate based on scan results

### Fix 3: Brute Force Prevention

**Vulnerability**: No rate limiting on login

**Attack**: Automated password guessing
```python
for password in wordlist:
    login(username='admin', password=password)
```

**Fix** (patched/app/routes/auth.py:21-30):
```python
# IP-based rate limiting
recent_failed_attempts_ip = FailedLoginTracker.get_recent_by_ip(ip_address, minutes=10)
if len(recent_failed_attempts_ip) >= 10:
    flash('Too many failed login attempts. Please try again later.', 'danger')
    return render_template('login.html'), 429

# Username-based rate limiting
recent_failed_attempts_user = FailedLoginTracker.get_recent_by_username(username, minutes=15)
if len(recent_failed_attempts_user) >= 5:
    flash('Account temporarily locked due to multiple failed login attempts.', 'danger')
    return render_template('login.html'), 403
```

**Additional Protection**:
- Failed attempts logged to database
- Auto-response rules can block IP or lock account
- Admin notified of brute force attempts
- Warning shown on successful login if previous failures

### Fix 4: Missing Security Middleware

**Vulnerability**: No global security checks

**Fix** (patched/app/app.py:27-33):
```python
from app.utils.security_middleware import security_checks, log_404_handler

@app.before_request
def before_request_security():
    return security_checks()

@app.errorhandler(404)
def handle_404(error):
    return log_404_handler(error)
```

**What It Does**:
- Checks IP blocklist before every request
- Validates user lock status
- Detects suspicious user agents
- Monitors cookie manipulation
- Tracks session anomalies
- Logs directory brute force (404s)

### Fix 5: Comprehensive Attack Logging

**Vulnerability**: Minimal attack logging

**Fix**: Extended attack_logs table with:
- classification (attack stage)
- recommended_action (what to do)
- action_taken (what was done)
- risk_score (0-100)
- related_attack_id (attack chains)
- raw_request_data (full details)
- reverse_action_steps (how to undo)

**Benefits**:
- Full incident response capability
- Attack chain analysis
- Automated response decisions
- Forensic investigation support
- Reversible security actions

---

## Request Flow

### Example: User Logs In

1. **Request arrives**: POST /login
2. **Security middleware** (before_request):
   - Check if IP is blocked → 403 if yes
   - Check for suspicious user agent → log if detected
   - Check for cookie manipulation → log if detected
3. **Route handler** (auth.py:login):
   - Get username and password from form
   - Check IP rate limit (10/10min) → 429 if exceeded
   - Check username rate limit (5/15min) → 403 if exceeded
   - Authenticate credentials (parameterized query)
   - Check if user account is locked → 403 if yes
   - Create session on success
   - Update last_login timestamp
   - Log failed attempt on failure
   - Check for previous failed attempts → warning if any
4. **Response**: Redirect to dashboard or show error

### Example: Admin Uploads Encrypted File

1. **Request arrives**: POST /upload/encrypted
2. **Security middleware**:
   - Check IP blocklist
   - Check user lock status
   - Validate session integrity
3. **Route handler** (upload.py:upload_encrypted):
   - Verify file provided
   - Sanitize filename with secure_filename()
   - Validate extension against whitelist
   - Check file size limit
   - Read file content
   - Encrypt using AES-CBC with random IV
   - Save encrypted file with .enc extension
   - Record upload in database
4. **Response**: Success message, redirect to upload page

### Example: Admin Decrypts File

1. **Request arrives**: POST /upload/encrypted/decrypt/<file_id>
2. **Security middleware**: Standard checks
3. **Route handler** (upload.py:decrypt_file):
   - Retrieve file metadata from database
   - Verify file exists and is encrypted
   - Read IV and encrypted content
   - Decrypt using AES-CBC
   - **SCAN DECRYPTED CONTENT**:
     - Check for malicious patterns
     - Validate MIME type
     - Check size limits
   - **Only save if all checks pass**
   - Return error if any check fails
4. **Response**: Success or error message

### Example: Attacker Attempts SQL Injection

1. **Request arrives**: POST /valves/search with payload `' OR 1=1--`
2. **Security middleware**: Standard checks
3. **Route handler** (valves.py:search_valves):
   - Get search term from form
   - **SQL injection detection**:
     - check_and_log_sql_injection() runs
     - Pattern matches OR statement
     - log_attack() called:
       - Calculate risk score (80)
       - Classify as "exploitation_exploitation"
       - Recommend action: "block_ip_permanent"
       - Store full request details
       - **Auto-response triggered**:
         - Check enabled rules for sql_injection
         - "Auto-block SQL injection" rule found
         - Threshold: 3 attempts in 60 minutes
         - Check recent attacks from IP
         - If threshold met → execute_block_ip()
           - Add to blocked_ips (24 hour)
           - Create security_action log
           - Update attack log
   - Flash error message
   - Redirect to valve list
4. **Response**: Error message, request blocked

### Example: Auto-Response Blocks IP

1. **Attack logged**: 3rd SQL injection attempt from 192.168.1.100
2. **auto_response.py:check_and_execute_auto_response()**:
   - Get enabled rules for attack type "sql_injection"
   - Find "Auto-block SQL injection" rule:
     - trigger_condition: "attack_count"
     - threshold: 3
     - time_window_minutes: 60
   - should_trigger_rule():
     - Get recent attacks from IP in last 60 minutes
     - Filter by attack_type = "sql_injection"
     - Count = 3
     - 3 >= 3 → return True
   - execute_action():
     - action_type = "block_ip"
     - execute_block_ip():
       - Check if already blocked → skip if yes
       - blocked_until = now + 24 hours
       - Create BlockedIP entry:
         - ip_address: 192.168.1.100
         - reason: "Auto-blocked: sql_injection - Rule: Auto-block SQL injection"
         - blocked_until: tomorrow
         - auto_unblock: True
       - Create SecurityAction log:
         - action_type: "block_ip"
         - automated: True
       - Update attack log:
         - action_taken: "ip_blocked_auto_24h"
3. **Result**: IP blocked for 24 hours
4. **Next request from 192.168.1.100**:
   - security_middleware:check_ip_blocked()
   - BlockedIP.is_blocked() returns entry
   - Return 403 JSON error
   - Request never reaches route handler

---

## Function Reference

### Security Functions

#### Attack Detection
- `detect_sql_injection(input_string)` → bool
- `detect_xss(input_string)` → bool
- `detect_path_traversal(input_string)` → bool
- `detect_file_upload_abuse(filename, content_type, file_size)` → list[str]
- `detect_suspicious_user_agent()` → (bool, str)
- `detect_directory_brute_force(ip_address)` → (bool, int)
- `detect_rate_limit_violation(ip_address, endpoint)` → (bool, int)
- `detect_session_anomaly(user_id, ip_address)` → (bool, str)
- `detect_cookie_manipulation()` → (bool, str)
- `detect_privilege_escalation(user_role, endpoint)` → (bool, str)

#### Attack Logging
- `log_attack(attack_type, endpoint, payload, severity, ...)` → int (attack_id)
- `check_and_log_sql_injection(search_term, endpoint)` → bool
- `check_and_log_xss(input_data, endpoint, field_name)` → bool
- `check_and_log_path_traversal(path, endpoint)` → bool
- `check_and_log_file_upload(filename, content_type, file_size, endpoint)` → bool
- `check_and_log_suspicious_agent(endpoint)` → bool
- `check_and_log_rate_limit(endpoint)` → bool
- `check_and_log_privilege_escalation(endpoint)` → bool
- `check_and_log_session_anomaly()` → bool
- `check_and_log_cookie_manipulation()` → bool

#### Auto-Response
- `check_and_execute_auto_response(attack_id, attack_type, ip_address, user_id, risk_score)` → None
- `should_trigger_rule(rule, attack_type, ip_address, user_id, risk_score)` → bool
- `execute_action(action_type, rule, attack_id, ip_address, user_id, attack_type_name)` → None
- `execute_block_ip(ip_address, rule, attack_id, attack_type_name)` → None
- `execute_lock_account(user_id, rule, attack_id, attack_type_name)` → None
- `execute_alert_admin(ip_address, user_id, rule, attack_id, attack_type_name)` → None
- `execute_rate_limit(ip_address, rule, attack_id, attack_type_name)` → None

#### Middleware
- `check_ip_blocked()` → Response or None
- `check_user_locked()` → Response or None
- `track_ip_in_session()` → None
- `security_checks()` → Response or None
- `log_404_handler(error)` → Response

#### Risk Assessment
- `calculate_risk_score(attack_type, ip_address, user_id, endpoint)` → int (0-100)
- `classify_attack(attack_type, endpoint, payload)` → (str, str)
- `recommend_action(attack_type, risk_score, attack_count)` → (str, list[str])

### Database Functions

#### User Management
- `User.create(username, password, role, email)` → int (user_id)
- `User.authenticate(username, password)` → dict or None
- `User.get_by_id(user_id)` → dict or None
- `User.update_last_login(user_id)` → None

#### Valve Operations
- `Valve.get_all()` → list[dict]
- `Valve.get_by_id(valve_id)` → dict or None
- `Valve.search(search_term)` → list[dict]
- `Valve.update_status(valve_id, open_percentage, command, user_id)` → None
- `Valve.update_communication_status(valve_id, status)` → None

#### Logging
- `CommandLog.create(valve_id, command, user_id, target_percentage, status, ...)` → int
- `CommandLog.get_by_valve(valve_id, limit)` → list[dict]
- `CommandLog.get_all(limit)` → list[dict]
- `CommandLog.get_failed(limit)` → list[dict]
- `CommandLog.get_timeouts(limit)` → list[dict]

#### Scheduling
- `Schedule.create(valve_id, scheduled_time, command, target_percentage, created_by)` → int
- `Schedule.get_all()` → list[dict]
- `Schedule.get_pending()` → list[dict]
- `Schedule.cancel(schedule_id)` → None

#### File Management
- `FileUpload.create(original_filename, stored_filename, ...)` → int
- `FileUpload.get_all()` → list[dict]

#### Security Management
- `BlockedIP.create(ip_address, reason, ...)` → int
- `BlockedIP.is_blocked(ip_address)` → dict or None
- `BlockedIP.unblock(ip_address)` → None
- `BlockedIP.get_all_active()` → list[dict]
- `BlockedIP.cleanup_expired()` → None
- `FailedLoginTracker.create(username, ip_address, ...)` → int
- `FailedLoginTracker.get_recent_by_username(username, minutes)` → list[dict]
- `FailedLoginTracker.get_recent_by_ip(ip_address, minutes)` → list[dict]
- `SecurityAction.create(action_type, target, reason, ...)` → int
- `SecurityAction.reverse_action(action_id, reversed_by)` → None
- `SecurityAction.get_all(limit)` → list[dict]
- `SecurityAction.get_active()` → list[dict]
- `AutoResponseRule.get_all()` → list[dict]
- `AutoResponseRule.get_enabled()` → list[dict]
- `AutoResponseRule.get_by_attack_type(attack_type)` → list[dict]
- `AutoResponseRule.toggle_enabled(rule_id)` → None
- `AutoResponseRule.update_threshold(rule_id, threshold)` → None
- `UserLocked.lock_user(user_id, reason, ...)` → int
- `UserLocked.is_locked(user_id)` → dict or None
- `UserLocked.unlock_user(user_id)` → None
- `UserLocked.get_all_locked()` → list[dict]
- `AttackLog.create(attack_type, endpoint, ...)` → int
- `AttackLog.get_all(limit)` → list[dict]
- `AttackLog.get_by_ip(ip_address, limit)` → list[dict]
- `AttackLog.get_recent_by_ip(ip_address, minutes)` → list[dict]
- `AttackLog.get_high_risk(threshold, limit)` → list[dict]
- `AttackLog.get_actionable(limit)` → list[dict]
- `AttackLog.get_attack_chains(attack_id)` → list[dict]
- `AttackLog.mark_action_taken(attack_id, action_taken)` → None
- `AttackLog.get_by_type(attack_type, limit)` → list[dict]
- `AttackLog.get_statistics()` → dict

### Utility Functions

#### File Operations
- `get_file_extension(filename)` → str
- `validate_file_content(filepath)` → bool
- `secure_filename(filename)` → str (from werkzeug)

#### Authentication
- `generate_password_hash(password)` → str (from werkzeug)
- `check_password_hash(hash, password)` → bool (from werkzeug)

#### Decorators
- `@login_required` - Requires authentication
- `@admin_required` - Requires admin role
- `@operator_or_admin_required` - Requires operator or admin role

---

## Summary

The patched version implements a comprehensive security system with:

1. **Complete SQL Injection Prevention**: Parameterized queries throughout
2. **Secure File Uploads**: Multiple validation layers, decrypt-then-scan
3. **Brute Force Protection**: Rate limiting, account locks, IP blocks
4. **Real-Time Attack Detection**: Pattern matching, behavioral analysis
5. **Automated Incident Response**: Configurable rules, reversible actions
6. **Comprehensive Logging**: Full audit trails, attack chains, risk scoring
7. **Defense in Depth**: Multiple overlapping security controls

Every vulnerability in the original system has been systematically addressed with modern security best practices.
