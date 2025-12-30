# Phase 2 Complete: Vulnerable Version Cloned

## Overview

Phase 2 has been successfully completed! The secure baseline application has been cloned to create a separate vulnerable version. Both versions now exist as independent applications ready for Phase 3 (introducing vulnerabilities).

## What Was Accomplished

### ✅ Directory Structure Created

```
task_5_CS437/
├── docker-compose.yml              # Orchestration for both versions
├── patched/                        # Secure implementation (Phase 1)
│   ├── app/                        # Flask application
│   ├── database/valves.db          # 150 valve records
│   ├── uploads/                    # Secure file storage
│   ├── venv/                       # Python environment
│   ├── VERSION.txt                 # "PATCHED VERSION"
│   └── run.py                      # Port 5001
└── vulnerable/                     # Clone for vulnerabilities (Phase 3)
    ├── app/                        # Flask application (identical to patched)
    ├── database/valves.db          # Fresh 150 valve records
    ├── uploads/                    # File storage
    ├── venv/                       # Python environment
    ├── VERSION.txt                 # "VULNERABLE VERSION"
    └── run.py                      # Port 5000
```

### ✅ Independent Configuration

**Patched Version (Secure):**
- Port: 5001
- Status: Secure baseline
- Features: All security controls active
- Database: Independent SQLite database
- Purpose: Reference implementation + testing patched endpoints

**Vulnerable Version (To Be Weakened):**
- Port: 5000
- Status: Currently secure (Phase 3 will introduce flaws)
- Features: Identical to patched (for now)
- Database: Independent SQLite database
- Purpose: Demonstrate vulnerabilities + exploitation

### ✅ Version Identification

Created `VERSION.txt` files in each directory:

**vulnerable/VERSION.txt:**
```
VULNERABLE VERSION - FOR EDUCATIONAL PURPOSES ONLY

This version contains intentional security vulnerabilities:
- CWE-434: Unrestricted File Upload (3 scenarios)
- SQL Injection: Role-based conditional escaping

DO NOT deploy this version in production environments.

Port: 5000
Status: Intentionally Vulnerable
```

**patched/VERSION.txt:**
```
PATCHED VERSION - SECURE IMPLEMENTATION

This version implements proper security controls:
- Secure file upload validation
- Parameterized SQL queries
- Input sanitization
- Attack detection and monitoring

This is the secure reference implementation.

Port: 5001
Status: Secure
```

### ✅ Docker Compose Configuration

Created `docker-compose.yml` to run both versions simultaneously:

```yaml
services:
  vulnerable:
    build: ./vulnerable
    ports: "5000:5000"
    
  patched:
    build: ./patched
    ports: "5001:5000"
```

**Benefits:**
- One-command deployment: `docker-compose up --build`
- Isolated containers
- Separate volumes for data persistence
- Network isolation
- Easy switching between versions for comparison

### ✅ Database Initialization

Both versions have:
- ✅ Fresh SQLite databases created
- ✅ 150 valve records populated (V-001 to V-150)
- ✅ 2 users (admin/admin123, operator/operator123)
- ✅ 50 command log entries
- ✅ 10 scheduled operations

**Independence:** Changes to one database don't affect the other, allowing:
- Clean exploitation testing on vulnerable version
- Secure baseline verification on patched version
- Direct comparison of attack impacts

### ✅ Dependencies Installed

Both versions have:
- Flask 3.0.0
- Flask-Session 0.5.0
- Werkzeug 3.0.1
- Jinja2 3.1.2
- pycryptodome 3.19.0
- python-magic 0.4.27

## Project Status

### Completed Phases
1. ✅ **Phase 0**: Architecture & Design
2. ✅ **Phase 1**: Secure Baseline Application  
3. ✅ **Phase 2**: Clone to Vulnerable Version

### Current State

**File Count:**
- Python files: 22 (11 per version)
- HTML templates: 16 (8 per version)
- Configuration files: 8 (4 per version)
- Total lines of code: ~3,500+

**Both Versions Functional:**
- Authentication working
- Dashboard operational
- Valve control active
- Scheduling system ready
- File upload prepared (secure for now)
- Monitoring dashboard operational
- Logging systems active

## Next Steps: Phase 3

**Goal:** Introduce 4 required vulnerabilities in the vulnerable version only

### Vulnerabilities to Implement:

1. **CWE-434 Scenario 1:** Unrestricted file upload
   - Remove ALL validation
   - Accept any file type, any size
   - Create endpoint: `/upload/scenario1`

2. **CWE-434 Scenario 2:** Weak protections (2 mechanisms)
   - File size limit (bypassable)
   - Extension blacklist (bypassable)
   - Create endpoint: `/upload/scenario2`

3. **CWE-434 Scenario 3:** Encrypted file bypass
   - Scan plaintext only
   - Allow encrypted upload without re-scan after decryption
   - Create endpoint: `/upload/scenario3`

4. **SQL Injection:** Role-based conditional escaping
   - Admin: Raw SQL string concatenation
   - Operator: Parameterized queries
   - Same endpoint: `/valves/search`

### Files to Modify (Vulnerable Version Only):

1. `vulnerable/app/routes/upload.py` - Add 3 vulnerable upload scenarios
2. `vulnerable/app/routes/valves.py` - Modify search to use conditional escaping
3. `vulnerable/app/templates/upload.html` - Add forms for 3 scenarios

**Patched version remains unchanged** - serves as secure reference.

## Docker Deployment Ready

When ready to deploy both:

```bash
# Build and start both versions
docker-compose up --build

# Access:
# Vulnerable: http://localhost:5000
# Patched:    http://localhost:5001
```

## Technical Details

### Port Configuration

**Patched (run.py):**
```python
app.run(host='0.0.0.0', port=5001, debug=True)
```

**Vulnerable (run.py):**
```python
app.run(host='0.0.0.0', port=5000, debug=True)
```

### Separation Benefits

1. **Clean Testing**: Exploit vulnerable version without affecting patched
2. **Direct Comparison**: Run same attacks on both versions
3. **Code Review**: Easy diff between versions to see security changes
4. **Documentation**: Clear before/after examples
5. **Demo Preparation**: Switch between versions during presentation

## Verification Checklist

- [x] Vulnerable directory created
- [x] Patched directory unchanged
- [x] Both have independent databases
- [x] Both have separate virtual environments
- [x] Different ports configured (5000 vs 5001)
- [x] VERSION.txt files created
- [x] Docker-compose.yml created
- [x] Dependencies installed for both
- [x] Databases populated for both
- [x] Both versions functional

## Important Notes

⚠️ **Current Status**: Both versions are currently SECURE
- The vulnerable version is an exact copy of the patched version
- Phase 3 will introduce intentional security flaws ONLY in the vulnerable version
- The patched version will remain as the secure reference

⚠️ **Port Conflict Note**: 
- Port 5000 may conflict with macOS AirPlay Receiver
- Solution: Disable AirPlay Receiver or use Docker (handles port mapping)
- Alternative: Change vulnerable version to port 5002 if needed

## Success Metrics

✅ **Both versions can:**
- Run independently
- Access separate databases
- Handle 150 valve records
- Process user authentication
- Execute valve commands
- Upload files (securely, for now)
- Log activities
- Monitor for attacks

✅ **Ready for Phase 3:**
- Code structure in place
- Upload endpoints exist (secure)
- Search functionality exists (secure)
- Monitoring system functional
- Templates ready for modification

---

**Phase 2 Status: 100% Complete ✅**

Two independent, fully functional SCADA applications exist:
- **Patched**: Secure reference implementation
- **Vulnerable**: Ready for intentional security weakening

**Next Milestone**: Implement 4 required vulnerabilities in vulnerable version (Phase 3)

---

**Total Development Time So Far**: Phase 0 + Phase 1 + Phase 2 Complete
**Lines of Code**: ~3,500+
**Files Created**: 35+ per version
**Database Records**: 150 valves × 2 versions = 300 total valve records

