# Remote Valve Management System - System Architecture

## 1. System Overview

A Flask-based SCADA web interface for managing industrial valve networks. The system provides real-time monitoring, control, and scheduling capabilities for field valve operations.

**Purpose:** Demonstrate security vulnerabilities (CWE-434, SQL Injection) and their remediation in OT/SCADA environments.

---

## 2. Technology Stack

| Component | Technology | Justification |
|-----------|-----------|---------------|
| Backend | Flask (Python 3.9+) | Lightweight, easy to demonstrate vulnerabilities |
| Database | SQLite3 | Embedded, OT-friendly, simple Docker deployment |
| Frontend | HTML5 + Bootstrap 5 | Simple, industrial SCADA aesthetics |
| Authentication | Flask-Session | Standard session management |
| Encryption | PyCryptodome (AES) | For file upload scenario 3 |
| Container | Docker + docker-compose | Reproducible deployment |

---

## 3. System Architecture

```
┌─────────────────────────────────────────────────────┐
│                   Web Browser                       │
│              (Admin / Operator)                     │
└───────────────────┬─────────────────────────────────┘
                    │ HTTPS (HTTP for demo)
                    ▼
┌─────────────────────────────────────────────────────┐
│              Flask Application                       │
│  ┌──────────────────────────────────────────────┐  │
│  │         Authentication Layer                  │  │
│  └──────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────┐  │
│  │      Request Logging Middleware              │  │
│  │      (Attack Detection & Classification)     │  │
│  └──────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────┐  │
│  │           Route Handlers                      │  │
│  │  • Dashboard  • Valve Control                │  │
│  │  • Scheduling • File Upload                  │  │
│  │  • Logs       • Monitoring                   │  │
│  └──────────────────────────────────────────────┘  │
└─────────────────────┬───────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────┐
│              SQLite Database                         │
│  • users        • valves       • logs               │
│  • schedules    • uploads      • attack_logs        │
└─────────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────┐
│              File System                             │
│  • /uploads/firmware/                               │
│  • /uploads/configs/                                │
│  • /uploads/encrypted/                              │
└─────────────────────────────────────────────────────┘
```

---

## 4. Database Schema

### 4.1 Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('admin', 'operator')),
    email TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);
```

**Default Users:**
- admin / admin123 (role: admin)
- operator / operator123 (role: operator)

### 4.2 Valves Table (100+ records)
```sql
CREATE TABLE valves (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    valve_name TEXT UNIQUE NOT NULL,
    location TEXT NOT NULL,
    open_percentage INTEGER DEFAULT 0 CHECK(open_percentage BETWEEN 0 AND 100),
    status TEXT DEFAULT 'operational' CHECK(status IN ('operational', 'maintenance', 'error', 'offline')),
    communication_status TEXT DEFAULT 'connected' CHECK(communication_status IN ('connected', 'disconnected', 'timeout')),
    last_command TEXT,
    last_command_timestamp TIMESTAMP,
    last_response_timestamp TIMESTAMP,
    firmware_version TEXT DEFAULT '1.0.0',
    config_file TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Sample Data Pattern:**
- Valve names: V-001 through V-150
- Locations: Building-A through Building-E, Sector-1 through Sector-10
- Random open_percentage (0-100)
- Random status distribution

### 4.3 Command Logs Table
```sql
CREATE TABLE command_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    valve_id INTEGER NOT NULL,
    command TEXT NOT NULL,
    user_id INTEGER NOT NULL,
    target_percentage INTEGER,
    status TEXT CHECK(status IN ('success', 'failed', 'timeout')),
    response_time_ms INTEGER,
    error_message TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (valve_id) REFERENCES valves(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

### 4.4 Schedules Table
```sql
CREATE TABLE schedules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    valve_id INTEGER NOT NULL,
    scheduled_time TIMESTAMP NOT NULL,
    command TEXT NOT NULL,
    target_percentage INTEGER,
    created_by INTEGER NOT NULL,
    status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'executed', 'cancelled', 'failed')),
    executed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (valve_id) REFERENCES valves(id),
    FOREIGN KEY (created_by) REFERENCES users(id)
);
```

### 4.5 File Uploads Table
```sql
CREATE TABLE file_uploads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    original_filename TEXT NOT NULL,
    stored_filename TEXT NOT NULL,
    file_type TEXT CHECK(file_type IN ('firmware', 'config', 'encrypted')),
    file_size INTEGER NOT NULL,
    upload_endpoint TEXT NOT NULL,
    uploaded_by INTEGER NOT NULL,
    is_encrypted BOOLEAN DEFAULT 0,
    scan_status TEXT CHECK(scan_status IN ('pending', 'clean', 'malicious', 'skipped')),
    applied_to_valve INTEGER,
    upload_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (uploaded_by) REFERENCES users(id),
    FOREIGN KEY (applied_to_valve) REFERENCES valves(id)
);
```

### 4.6 Attack Logs Table (Monitoring System)
```sql
CREATE TABLE attack_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    attack_type TEXT NOT NULL CHECK(attack_type IN (
        'sql_injection', 
        'file_upload_abuse', 
        'size_bypass', 
        'mime_bypass',
        'encrypted_payload',
        'suspicious_activity'
    )),
    endpoint TEXT NOT NULL,
    user_id INTEGER,
    ip_address TEXT,
    user_agent TEXT,
    request_method TEXT,
    payload TEXT,
    severity TEXT CHECK(severity IN ('low', 'medium', 'high', 'critical')),
    blocked BOOLEAN DEFAULT 0,
    details TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

---

## 5. REST API Endpoints

### 5.1 Authentication
| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| GET | `/` | Public | Landing page, redirects to login |
| GET | `/login` | Public | Login form |
| POST | `/login` | Public | Authenticate user |
| GET | `/logout` | Authenticated | End session |

### 5.2 Dashboard & Monitoring
| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| GET | `/dashboard` | Authenticated | Main valve overview dashboard |
| GET | `/valves` | Authenticated | List all valves with status |
| GET | `/valve/<id>` | Authenticated | Detailed valve information |
| GET | `/monitoring` | Admin | Attack monitoring dashboard |
| GET | `/api/monitoring/stats` | Admin | Attack statistics (JSON) |

### 5.3 Valve Control
| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| POST | `/valve/<id>/control` | Operator, Admin | Open/close valve |
| POST | `/valve/<id>/sync` | Operator, Admin | Force re-synchronization |
| GET | `/valve/<id>/logs` | Authenticated | Command execution logs |

### 5.4 Scheduling
| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| GET | `/schedules` | Authenticated | View all schedules |
| POST | `/schedules/create` | Operator, Admin | Create new schedule |
| DELETE | `/schedules/<id>` | Admin | Cancel schedule |

### 5.5 File Uploads (Vulnerable Endpoints)
| Method | Endpoint | Access | Description | Vulnerability |
|--------|----------|--------|-------------|---------------|
| GET | `/upload/scenario1` | Admin | Upload form 1 | CWE-434: No validation |
| POST | `/upload/scenario1` | Admin | Process upload 1 | No file type/size checks |
| GET | `/upload/scenario2` | Admin | Upload form 2 | CWE-434: Weak protection |
| POST | `/upload/scenario2` | Admin | Process upload 2 | Size limit + blacklist (bypassable) |
| GET | `/upload/scenario3` | Admin | Upload form 3 | CWE-434: Encrypted bypass |
| POST | `/upload/scenario3` | Admin | Process upload 3 | Scans plaintext only |
| POST | `/upload/scenario3/decrypt` | Admin | Decrypt uploaded file | Post-scan decryption |

### 5.6 Search & Filtering (SQL Injection Vulnerability)
| Method | Endpoint | Access | Description | Vulnerability |
|--------|----------|--------|-------------|---------------|
| GET | `/valves/search` | Authenticated | Search valves | Role-based SQL injection |
| POST | `/valves/search` | Authenticated | Execute search | Admin=raw SQL, Operator=escaped |

### 5.7 Logs
| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| GET | `/logs/commands` | Authenticated | Command execution logs |
| GET | `/logs/failures` | Authenticated | Failed valve responses |
| GET | `/logs/timeouts` | Authenticated | Communication timeouts |

---

## 6. User Roles & Permissions

### 6.1 Admin Role
**Capabilities:**
- Full system access
- View all valves and logs
- Control all valves
- Create and cancel schedules
- Upload firmware and configuration files
- Access monitoring dashboard
- View attack logs

**Vulnerabilities:**
- SQL injection exploitable (raw SQL execution)
- Can upload dangerous files

### 6.2 Operator Role
**Capabilities:**
- View all valves and logs
- Control valves
- Create schedules (cannot cancel others')
- View command logs
- Upload configuration files (limited)

**Protections:**
- SQL queries are escaped (not vulnerable to SQLi)
- Limited file upload access

---

## 7. File Upload Workflows

### 7.1 Scenario 1: No Protection (Baseline Vulnerability)

**Workflow:**
```
User (Admin) → Upload Form → POST /upload/scenario1
                                    ↓
                          No validation performed
                                    ↓
                     File saved directly to /uploads/firmware/
                                    ↓
                          Success message returned
```

**Vulnerability:** Any file type, any size, executable location

### 7.2 Scenario 2: Weak Protection (Size + Blacklist)

**Workflow:**
```
User (Admin) → Upload Form → POST /upload/scenario2
                                    ↓
                          Check file size < 5MB
                                    ↓
                    Check extension NOT in blacklist
                    [.exe, .sh, .bat, .php]
                                    ↓
                          Validate MIME type
                    [only check Content-Type header]
                                    ↓
                     File saved to /uploads/firmware/
```

**Vulnerabilities:**
- Size limit bypassable (tamper with Content-Length header)
- Blacklist incomplete (e.g., .phtml, .php5, double extensions)
- MIME type easily spoofed (client-side header)

### 7.3 Scenario 3: Encrypted Bypass (Scan Evasion)

**Workflow:**
```
User (Admin) → Upload Encrypted File → POST /upload/scenario3
                                              ↓
                                   Check if plaintext
                                              ↓
                                   Run malware scan
                                   (only on plaintext)
                                              ↓
                          File saved to /uploads/encrypted/
                                              ↓
                        Admin triggers decryption later
                                              ↓
                        POST /upload/scenario3/decrypt
                                              ↓
                          Decrypt with AES key
                                              ↓
                     Save decrypted file (no scan!)
```

**Vulnerability:** Encrypted files bypass scanning, decrypted post-upload without re-scan

---

## 8. SQL Injection Vulnerability Design

### 8.1 Vulnerable Search Implementation

**Location:** `/valves/search` endpoint

**Vulnerable Code Logic:**
```python
if user.role == 'admin':
    query = f"SELECT * FROM valves WHERE valve_name LIKE '%{search_term}%'"
elif user.role == 'operator':
    query = "SELECT * FROM valves WHERE valve_name LIKE ?"
    params = (f'%{search_term}%',)
```

**Exploitation:**
- Admin user can inject: `V-001' UNION SELECT * FROM users--`
- Operator user: same input is safely parameterized

**Detection Challenge:**
- Low-privilege testing won't find this
- Only exploitable with admin credentials
- Same input field, different backend behavior

---

## 9. Monitoring System Design

### 9.1 Attack Detection Middleware

**Triggers:**
1. **SQL Injection Detection:**
   - Pattern matching: `UNION`, `OR 1=1`, `' --`, `';--`, etc.
   - Context: Search parameters, filter inputs
   
2. **File Upload Abuse:**
   - Suspicious extensions: `.php`, `.py`, `.exe`, `.sh`
   - Double extensions: `.php.jpg`, `.exe.png`
   - MIME mismatch: declares image, contains executable
   
3. **Size Bypass:**
   - Content-Length header doesn't match actual size
   - Chunked encoding manipulation
   
4. **Encrypted Payload:**
   - Files with encryption headers
   - Decryption requests without re-scan

### 9.2 Monitoring Dashboard

**Components:**
- Real-time attack counter
- Attack type breakdown (pie chart)
- Recent attacks table (last 50)
- Severity distribution
- Top targeted endpoints
- Attack timeline (last 24 hours)

**Data Displayed:**
- Timestamp
- Attack type
- User (if authenticated)
- IP address
- Endpoint
- Payload snippet
- Severity level
- Blocked status (patched version)

---

## 10. Logging Strategy

### 10.1 Events to Log

**Operational Events:**
- User login/logout
- Valve state changes
- Command executions (success/failure)
- Scheduled operations
- Communication timeouts
- Re-synchronization requests

**Security Events:**
- Failed login attempts
- SQL injection attempts
- Suspicious file uploads
- Role-based access violations
- Unusual query patterns

### 10.2 Log Storage

- **Operational logs:** `command_logs` table
- **Security logs:** `attack_logs` table
- **Application logs:** Flask logger (stdout for Docker)

---

## 11. Security Considerations (Patched Version)

### 11.1 File Upload Security

**Protections:**
1. **Allow-list validation:** Only `.bin` (firmware), `.conf` (config)
2. **Magic byte verification:** Check file headers, not just extension
3. **Size limits:** Hard limit enforced server-side
4. **Decrypt-then-scan:** Always scan after decryption
5. **Isolated storage:** Files outside web root
6. **Randomized filenames:** Prevent path traversal

### 11.2 SQL Injection Prevention

**Protections:**
1. **Parameterized queries:** All database operations use `?` placeholders
2. **ORM usage:** SQLAlchemy for complex queries
3. **Role-independent:** Same escaping logic for all users
4. **Input validation:** Whitelist allowed characters
5. **Prepared statements:** No string concatenation

### 11.3 Additional Hardening

- CSRF tokens on all POST requests
- Secure session cookies (HTTPOnly, Secure flags)
- Rate limiting on authentication
- Input length restrictions
- Error messages don't leak info
- Database connection pooling

---

## 12. Docker Architecture

### 12.1 Vulnerable Version Container

```
vulnerable/
├── Dockerfile
├── app/
│   ├── app.py
│   ├── models.py
│   ├── routes/
│   ├── templates/
│   ├── static/
│   └── utils/
├── requirements.txt
├── init_db.py
├── populate_db.py
└── database/
    └── valves.db (created on startup)
```

### 12.2 Patched Version Container

```
patched/
├── Dockerfile
├── app/
│   ├── app.py (secure implementation)
│   ├── models.py
│   ├── routes/
│   ├── templates/
│   ├── static/
│   └── utils/
├── requirements.txt
├── init_db.py
├── populate_db.py
└── database/
    └── valves.db (created on startup)
```

### 12.3 docker-compose.yml

```yaml
version: '3.8'
services:
  vulnerable:
    build: ./vulnerable
    ports:
      - "5000:5000"
    volumes:
      - vulnerable_data:/app/database
      - vulnerable_uploads:/app/uploads
    environment:
      - FLASK_ENV=development
      
  patched:
    build: ./patched
    ports:
      - "5001:5000"
    volumes:
      - patched_data:/app/database
      - patched_uploads:/app/uploads
    environment:
      - FLASK_ENV=development
```

---

## 13. Dependencies

### 13.1 Python Requirements

```
Flask==3.0.0
Flask-Session==0.5.0
Werkzeug==3.0.1
Jinja2==3.1.2
pycryptodome==3.19.0
python-magic==0.4.27
```

### 13.2 System Dependencies (Docker)

```
python:3.9-slim
libmagic1 (for file type detection)
```

---

## 14. Development Phases Summary

1. **Phase 0:** ✅ Architecture design (this document)
2. **Phase 1:** Build secure baseline application
3. **Phase 2:** Clone to vulnerable version
4. **Phase 3:** Implement vulnerabilities
5. **Phase 4:** Build monitoring system
6. **Phase 5:** Verify patched version security
7. **Phase 6:** Dockerize both versions
8. **Phase 7:** Testing with pentesting tools
9. **Phase 8:** Documentation and video

---

## 15. Success Criteria

### Functional Requirements
- ✅ 100+ valve records in database
- ✅ User authentication with 2 roles
- ✅ Full SCADA operations (view, control, schedule)
- ✅ File upload functionality (3 scenarios)
- ✅ Search/filter with SQL injection vulnerability
- ✅ Monitoring dashboard with attack classification

### Security Requirements
- ✅ 4 distinct exploitable vulnerabilities (vulnerable version)
- ✅ All vulnerabilities patchable with standard techniques
- ✅ Exploitable with Burp Suite and sqlmap
- ✅ Monitoring system logs all attacks
- ✅ Patched version blocks all exploits

### Deployment Requirements
- ✅ Both versions run in Docker
- ✅ Single command deployment (`docker-compose up`)
- ✅ Database auto-populated on startup
- ✅ No manual configuration needed

---

**Architecture Status:** ✅ Complete  
**Ready for Phase 1:** Yes  
**Next Action:** Implement secure baseline Flask application

