# Startup Guide - Remote Valve Management System

## Quick Start - Running Both Versions

### Option 1: Docker (Recommended)

Run both versions simultaneously:

```bash
# From project root
docker-compose up --build

# Access:
# Vulnerable: http://localhost:5000
# Patched:    http://localhost:5001
```

Stop both:
```bash
docker-compose down
```

### Option 2: Local Development

#### Running Patched Version (Port 5001)

```bash
cd patched
source venv/bin/activate
python run.py
```

Access: http://localhost:5001

#### Running Vulnerable Version (Port 5000)

```bash
cd vulnerable
source venv/bin/activate  
python run.py
```

Access: http://localhost:5000

**Note:** On macOS, port 5000 may conflict with AirPlay Receiver. 
Disable it in: System Preferences → General → AirDrop & Handoff

## Default Credentials

Both versions use the same credentials:

| Username | Password | Role |
|----------|----------|------|
| admin | admin123 | Administrator |
| operator | operator123 | Operator |

## Database Information

### Location
- **Patched:** `patched/database/valves.db`
- **Vulnerable:** `vulnerable/database/valves.db`

### Contents (Both)
- 150 valve records (V-001 to V-150)
- 2 users (admin, operator)
- 50 command log entries
- 10 scheduled operations

### Reset Database

If you need to reset either database:

```bash
# For patched version
cd patched
rm database/valves.db
python init_db.py
python populate_db.py

# For vulnerable version
cd vulnerable
rm database/valves.db
python init_db.py
python populate_db.py
```

## Version Differences (Current State)

### Patched Version ✅
- **Port:** 5001
- **Status:** Secure implementation
- **Features:** All security controls active
- **File:** `patched/VERSION.txt`

**Security Features:**
- Parameterized SQL queries
- File type whitelist validation
- Magic byte checking
- Size limit enforcement
- Input sanitization
- Attack detection & monitoring

### Vulnerable Version ⚠️
- **Port:** 5000
- **Status:** Currently secure (Phase 3 will add vulnerabilities)
- **Features:** Identical to patched (for now)
- **File:** `vulnerable/VERSION.txt`

**Planned Vulnerabilities (Phase 3):**
- CWE-434 Scenario 1: No file validation
- CWE-434 Scenario 2: Weak size/blacklist checks
- CWE-434 Scenario 3: Encrypted file bypass
- SQL Injection: Role-based conditional escaping

## Directory Structure

```
task_5_CS437/
├── docker-compose.yml          # Run both versions
├── STARTUP_GUIDE.md           # This file
├── ARCHITECTURE.md            # System design
├── README.md                  # Project overview
├── todo.md                    # Development progress
├── patched/                   # Secure version
│   ├── run.py                # Entry point (port 5001)
│   ├── app/                  # Flask application
│   ├── database/             # SQLite database
│   └── venv/                 # Python environment
└── vulnerable/               # Vulnerable version
    ├── run.py                # Entry point (port 5000)
    ├── app/                  # Flask application
    ├── database/             # SQLite database
    └── venv/                 # Python environment
```

## Testing & Development

### Check if Running

```bash
# Check patched version
curl http://localhost:5001/

# Check vulnerable version  
curl http://localhost:5000/
```

### View Logs

When running locally, logs appear in the terminal.

### Stop Running Servers

Press `Ctrl+C` in the terminal where Flask is running.

### Port Status

```bash
# Check what's using port 5000
lsof -i :5000

# Check what's using port 5001
lsof -i :5001
```

## Common Issues

### Port 5000 Already in Use (macOS)

**Problem:** AirPlay Receiver uses port 5000

**Solutions:**
1. Disable AirPlay Receiver:
   - System Preferences → General → AirDrop & Handoff
   - Turn off "AirPlay Receiver"

2. Use Docker (port mapping handles this)

3. Change vulnerable version port in `vulnerable/run.py`:
   ```python
   app.run(host='0.0.0.0', port=5002, debug=True)
   ```

### Database Locked Error

**Problem:** Database is being accessed by another process

**Solution:**
```bash
# Find process using database
lsof | grep valves.db

# Kill the process or restart the application
```

### Module Not Found Errors

**Problem:** Virtual environment not activated or dependencies not installed

**Solution:**
```bash
# Activate venv
source venv/bin/activate  # or source patched/venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Template Not Found

**Problem:** Running from wrong directory

**Solution:** Always run `python run.py` from the version's root directory (patched/ or vulnerable/)

## Development Workflow

### Making Changes to Patched Version

1. Edit files in `patched/app/`
2. Flask auto-reloads (debug mode)
3. Refresh browser to see changes

### Making Changes to Vulnerable Version

1. Edit files in `vulnerable/app/`
2. Flask auto-reloads (debug mode)
3. Refresh browser to see changes

### Comparing Versions

```bash
# Compare specific files
diff patched/app/routes/upload.py vulnerable/app/routes/upload.py

# Compare directories
diff -r patched/app/ vulnerable/app/
```

## Next Steps

After Phase 3 (vulnerabilities implemented), you'll be able to:

1. **Test Vulnerabilities** (Vulnerable Version - Port 5000):
   - Upload malicious files
   - Perform SQL injection
   - Bypass file filters
   - Test encrypted payload bypass

2. **Verify Patches** (Patched Version - Port 5001):
   - Confirm attacks are blocked
   - Check monitoring logs
   - Verify secure behavior

3. **Compare Side-by-Side**:
   - Run same attack on both
   - Document differences
   - Screenshot results

## Monitoring Dashboard

**Access:** http://localhost:5001/monitoring (Admin only)

**Features:**
- Real-time attack detection
- Attack classification
- Severity tracking
- Request details
- IP logging

## Useful Commands

```bash
# Start fresh with both versions
docker-compose down -v  # Remove volumes
docker-compose up --build

# View Docker logs
docker-compose logs vulnerable
docker-compose logs patched

# Access Docker container
docker exec -it scada_vulnerable /bin/bash
docker exec -it scada_patched /bin/bash

# Rebuild specific version
docker-compose build vulnerable
docker-compose build patched
```

## File Upload Endpoints (Post-Phase 3)

### Vulnerable Version (Port 5000)
- `/upload/scenario1` - No validation (CWE-434 #1)
- `/upload/scenario2` - Weak checks (CWE-434 #2)
- `/upload/scenario3` - Encrypted bypass (CWE-434 #3)

### Patched Version (Port 5001)
- `/upload/secure` - Full validation
- `/upload/encrypted` - Decrypt-then-scan

## Support

- **Architecture:** See `ARCHITECTURE.md`
- **Progress:** See `todo.md`
- **Phase Summaries:** See `PHASE1_SUMMARY.md`, `PHASE2_SUMMARY.md`
- **Task Requirements:** See `task.md`

---

**Happy Testing! 🚀**

Remember: The vulnerable version is for educational purposes only. Never deploy it in production!

