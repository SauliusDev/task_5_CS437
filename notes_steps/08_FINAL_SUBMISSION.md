# Step 8: Final Submission Package

**Time Required:** 2-3 hours  
**Who:** All 3 team members (final review together)  
**Goal:** Package all deliverables and verify completeness before submission

## Overview

The submission package must include:
1. Source code (vulnerable + patched)
2. Docker configuration
3. Database and population script
4. Final report (PDF)
5. Video demonstration (link)
6. README with setup instructions

## Part A: Submission Requirements Checklist

### From Assignment Requirements:

**Required Deliverables:**
- [x] Report explaining vulnerabilities, exploitation, and patches
- [x] Vulnerable source code + requirements.txt
- [x] Patched source code + requirements.txt
- [x] Dockerized vulnerable version
- [x] Dockerized patched version
- [x] Video explaining application and vulnerabilities
- [x] Database with ≥100 records (have 150)
- [x] Population script (populate_db.py)

**Additional Requirements Met:**
- [x] Each vulnerability on separate page/endpoint
- [x] Monitoring system in both versions
- [x] Attack logging and classification
- [x] Pentesting tools demonstrated (Burp Suite, sqlmap)
- [x] No forced/illogical vulnerabilities

## Part B: File Structure Organization

### Create Submission Folder

```bash
cd /Users/azuolasbalbieris/Documents/Academic/Cybersecurity/task_5_CS437

# Create clean submission folder
mkdir -p submission_package
cd submission_package
```

### 1. Copy Source Code

```bash
# Vulnerable version
cp -r ../vulnerable ./vulnerable
rm -rf ./vulnerable/__pycache__
rm -rf ./vulnerable/app/__pycache__
rm -rf ./vulnerable/app/routes/__pycache__
rm -rf ./vulnerable/app/utils/__pycache__
rm -rf ./vulnerable/venv
rm -rf ./vulnerable/uploads/firmware/*
rm -rf ./vulnerable/uploads/configs/*
rm -rf ./vulnerable/uploads/encrypted/*

# Patched version
cp -r ../patched ./patched
rm -rf ./patched/__pycache__
rm -rf ./patched/app/__pycache__
rm -rf ./patched/app/routes/__pycache__
rm -rf ./patched/app/utils/__pycache__
rm -rf ./patched/venv
rm -rf ./patched/uploads/firmware/*
rm -rf ./patched/uploads/configs/*
rm -rf ./patched/uploads/encrypted/*
```

### 2. Copy Docker Files

```bash
# Root docker-compose
cp ../docker-compose.yml ./

# Vulnerable Dockerfile
cp ../vulnerable/Dockerfile ./vulnerable/
cp ../vulnerable/.dockerignore ./vulnerable/

# Patched Dockerfile
cp ../patched/Dockerfile ./patched/
cp ../patched/.dockerignore ./patched/
```

### 3. Copy Database Files

```bash
# Keep databases (they have 150 records)
# Already in vulnerable/database/ and patched/database/

# Verify record counts
sqlite3 vulnerable/database/valves.db "SELECT COUNT(*) FROM valves;"
# Should output: 150

sqlite3 patched/database/valves.db "SELECT COUNT(*) FROM valves;"
# Should output: 150
```

### 4. Copy Scripts

```bash
# Population script
cp ../populate_db.py ./

# Init script
cp ../init_db.py ./

# Migration script (if used)
cp ../migrate_database.py ./

# Run script
cp ../vulnerable/run.py ./vulnerable/
cp ../patched/run.py ./patched/
```

### 5. Copy Documentation

```bash
# Main README
cp ../README.md ./

# Startup guide
cp ../STARTUP_GUIDE.md ./

# Architecture
cp ../ARCHITECTURE.md ./

# Version files
cp ../vulnerable/VERSION.txt ./vulnerable/
cp ../patched/VERSION.txt ./patched/
```

## Part C: Create Comprehensive README

**File:** `submission_package/README.md`

```bash
cat > submission_package/README.md << 'EOF'
# CS 437 Assignment - Task 5: Remote Valve Management System

## Team Information
- **Team Members:**
  - [Name 1] - [Student ID] - [Email]
  - [Name 2] - [Student ID] - [Email]
  - [Name 3] - [Student ID] - [Email]

- **Task:** Task 5 - Remote Valve Management System
- **Submission Date:** [Date]
- **Assignment:** Develop, Exploit, and Patch Vulnerable SCADA Interface

## Project Overview

This project implements a SCADA (Supervisory Control and Data Acquisition) web application for managing 150 valves in a city water reservoir system. Two versions are provided:

1. **Vulnerable Version:** Contains 4 intentional security vulnerabilities
2. **Patched Version:** All vulnerabilities remediated with secure coding practices

## Vulnerabilities Implemented

1. **CWE-434 Scenario 1:** Unrestricted File Upload (No Protection)
2. **CWE-434 Scenario 2:** Weak File Upload Protection (Bypassable)
3. **CWE-434 Scenario 3:** Encrypted File Scanning Bypass
4. **SQL Injection:** Role-Based Conditional Escaping

## Quick Start

### Prerequisites
- Docker Desktop (20.10+)
- 4GB RAM available
- 10GB disk space
- Modern web browser (Firefox/Chrome)

### Installation & Running

1. **Extract submission package:**
```bash
unzip CS437_Task5_TeamX.zip
cd submission_package
```

2. **Start both applications:**
```bash
docker-compose up --build
```

This will start:
- Vulnerable version on port 5002
- Patched version on port 5001

3. **Access applications:**
- Vulnerable: http://localhost:5002
- Patched: http://localhost:5001

4. **Login credentials:**
- Admin: `admin` / `admin123`
- Operator: `operator1` / `operator123`
- Viewer: `viewer1` / `viewer123`

### Stopping Applications

```bash
docker-compose down
```

## Testing the Vulnerabilities

### Prerequisites for Testing
- Burp Suite Community Edition
- sqlmap
- curl

### Test Endpoints

**Vulnerable Version:**
- Upload Scenario 1: http://localhost:5002/upload/scenario1
- Upload Scenario 2: http://localhost:5002/upload/scenario2
- Upload Scenario 3: http://localhost:5002/upload/scenario3
- Valve Search (SQL Injection): http://localhost:5002/valves/search

**Monitoring Dashboard:**
- Vulnerable: http://localhost:5002/monitoring (admin only)
- Patched: http://localhost:5001/monitoring (admin only)

### Quick Vulnerability Tests

**1. File Upload (Scenario 1):**
```bash
echo '<?php echo "test"; ?>' > test.php
curl -X POST http://localhost:5002/upload/scenario1 \
  -F "file=@test.php" \
  -H "Cookie: session=YOUR_SESSION"
```

**2. SQL Injection (as admin):**
```bash
curl -X POST http://localhost:5002/valves/search \
  -d "search=' UNION SELECT id,username,password_hash,role,email,created_at,last_login,NULL FROM users--" \
  -H "Cookie: session=ADMIN_SESSION"
```

**3. sqlmap Test:**
```bash
sqlmap -u "http://localhost:5002/valves/search" \
  --data "search=test" \
  --cookie="session=ADMIN_SESSION" \
  --batch --dbs
```

See STARTUP_GUIDE.md for detailed testing instructions.

## File Structure

```
submission_package/
├── README.md                    # This file
├── STARTUP_GUIDE.md            # Detailed setup instructions
├── ARCHITECTURE.md             # System architecture
├── docker-compose.yml          # Docker orchestration
├── populate_db.py              # Database population script
├── init_db.py                  # Database initialization
├── REPORT.pdf                  # Complete project report
├── VIDEO_LINK.txt              # Link to demonstration video
├── vulnerable/                 # Vulnerable version
│   ├── app/
│   │   ├── app.py             # Main application
│   │   ├── models.py          # Database models
│   │   ├── routes/            # Route handlers
│   │   │   ├── auth.py        # Authentication
│   │   │   ├── dashboard.py  # Dashboard
│   │   │   ├── upload.py     # File uploads (VULNERABLE)
│   │   │   ├── valves.py     # Valve control (SQL injection)
│   │   │   ├── logs.py       # Logging
│   │   │   └── monitoring.py # Monitoring
│   │   ├── templates/         # HTML templates
│   │   ├── static/            # CSS/JS
│   │   └── utils/             # Utility functions
│   ├── database/
│   │   └── valves.db          # Database (150 records)
│   ├── uploads/               # Upload directories
│   ├── Dockerfile             # Docker build file
│   ├── requirements.txt       # Python dependencies
│   ├── run.py                 # Entry point
│   └── VERSION.txt            # Version info
├── patched/                    # Patched version (same structure)
│   └── (same structure as vulnerable/)
└── testing_evidence/           # Optional: testing screenshots
    └── (screenshots and outputs)
```

## Database Information

### Schema
- **users:** 4 user accounts (admin, operator1, operator2, viewer1)
- **valves:** 150 valve records (various types and locations)
- **command_logs:** Command execution history
- **attack_logs:** Security event monitoring
- **scheduled_operations:** Scheduled valve operations

### Population
Database is pre-populated. To reset:

```bash
cd vulnerable  # or patched
python3 init_db.py
python3 populate_db.py
```

## Security Features

### Vulnerable Version
- ✗ No file validation (Scenario 1)
- ✗ Weak file validation (Scenario 2)
- ✗ Scan before encryption (Scenario 3)
- ✗ Raw SQL for admin users
- ✓ Attack logging (but attacks allowed)

### Patched Version
- ✓ Whitelist-based file validation
- ✓ Magic byte verification
- ✓ Secure filename generation
- ✓ Decrypt-then-scan pipeline
- ✓ Parameterized SQL queries (all users)
- ✓ Input validation
- ✓ Attack logging and blocking

## Technology Stack

- **Backend:** Python 3.14, Flask 3.0
- **Database:** SQLite 3
- **Session:** Flask-Session (server-side)
- **Password Hashing:** PBKDF2-SHA256 (600k iterations)
- **Encryption:** AES-256-CBC (PyCryptodome)
- **File Validation:** python-magic
- **Deployment:** Docker, docker-compose

## Monitoring System

Both versions include a comprehensive monitoring system:
- Real-time attack detection
- Classification by attack type
- Complete request logging
- User and IP tracking
- Dashboard visualization

Access at `/monitoring` (admin only).

## Documentation

### Included Files:
- **REPORT.pdf** - Complete 30-40 page report covering:
  - Vulnerability descriptions
  - Exploitation methodology
  - Tool usage (Burp Suite, sqlmap)
  - Patching strategies
  - Testing results
  
- **VIDEO_LINK.txt** - Link to 12-15 minute demonstration video showing:
  - Application overview
  - Live exploitation of all vulnerabilities
  - Tool demonstrations
  - Monitoring system
  - Patched version verification

- **STARTUP_GUIDE.md** - Detailed setup and testing instructions

- **ARCHITECTURE.md** - System architecture and design decisions

## Testing Tools Used

- **Burp Suite Community Edition** - HTTP interception and manipulation
- **sqlmap** - Automated SQL injection testing
- **curl** - Command-line HTTP testing
- **Browser DevTools** - Manual testing and inspection

## Troubleshooting

### Port Already in Use
```bash
docker-compose down
lsof -ti:5001,5002 | xargs kill -9
docker-compose up --build
```

### Database Not Initialized
```bash
cd vulnerable
python3 init_db.py
python3 populate_db.py
```

### Session Expired
- Login again in browser
- Get fresh session cookie from browser DevTools

### Docker Build Fails
```bash
docker-compose down -v
docker system prune -a
docker-compose up --build
```

## Contact Information

For questions or issues:
- [Name 1]: [email1@sabanciuniv.edu]
- [Name 2]: [email2@sabanciuniv.edu]
- [Name 3]: [email3@sabanciuniv.edu]

## License

This project is for educational purposes as part of CS 437 - Operational Technology Security course at Sabancı University.

## Acknowledgments

- Course Instructor: [Instructor Name]
- Teaching Assistants: [TA Names]
- Sabancı University Faculty of Engineering and Natural Sciences

---

**Important Notes:**
1. This system contains intentional vulnerabilities for educational purposes
2. DO NOT deploy the vulnerable version in production environments
3. The patched version demonstrates secure coding practices
4. All vulnerabilities are documented in the report

**Testing Credentials:**
- Admin: admin / admin123 (for testing SQL injection)
- Operator: operator1 / operator123 (safe from SQL injection)

**Demonstration Video:** See VIDEO_LINK.txt for access link

**Report:** See REPORT.pdf for comprehensive documentation
EOF
```

## Part D: Create Video Link File

```bash
cat > submission_package/VIDEO_LINK.txt << 'EOF'
CS 437 Task 5 - Demonstration Video

Video Link: [INSERT YOUR YOUTUBE/DRIVE LINK HERE]

Video Length: [X] minutes
Format: MP4, 1920x1080, 30fps

Alternative Link (if primary fails): [BACKUP LINK]

Video Password (if protected): [PASSWORD]

Video Contents:
- Introduction and team presentation
- Application overview
- Demonstration of all 4 vulnerabilities
- Tool usage (Burp Suite, sqlmap)
- Monitoring system explanation
- Patched version verification
- Code comparison
- Conclusion

Team Members:
- [Name 1]
- [Name 2]
- [Name 3]

Upload Date: [DATE]
Estimated File Size: [SIZE]

Note: Video is set to "Unlisted" on YouTube (accessible via link only)
      or shared with "Anyone with link" access on Google Drive/OneDrive.

If video link is inaccessible, please contact:
- [Name]: [Email] - [Phone]
EOF
```

## Part E: Final Report Checklist

Verify your REPORT.pdf includes:

**Essential Sections:**
- [ ] Title page with team names
- [ ] Table of contents
- [ ] Executive summary
- [ ] System architecture (2-3 pages)
- [ ] Environment setup (1-2 pages)
- [ ] Vulnerability 1: CWE-434 Scenario 1 (5-6 pages)
- [ ] Vulnerability 2: CWE-434 Scenario 2 (5-6 pages)
- [ ] Vulnerability 3: CWE-434 Scenario 3 (5-6 pages)
- [ ] Vulnerability 4: SQL Injection (6-7 pages)
- [ ] Monitoring system (2-3 pages)
- [ ] Testing methodology (2-3 pages)
- [ ] Security patches (3-4 pages)
- [ ] Conclusions (1-2 pages)
- [ ] References
- [ ] Appendices

**For Each Vulnerability:**
- [ ] Description
- [ ] Vulnerable code snippet
- [ ] Root cause explanation
- [ ] Exploitation steps with tools
- [ ] 5-7 screenshots showing exploitation
- [ ] Impact analysis (OT-specific)
- [ ] Patched code snippet
- [ ] Explanation of fixes
- [ ] Verification screenshots (patched blocking)
- [ ] Monitoring screenshots

**Quality Checks:**
- [ ] 30-40 pages total
- [ ] All screenshots clear and annotated
- [ ] Code snippets syntax highlighted
- [ ] Professional formatting
- [ ] No spelling/grammar errors
- [ ] Page numbers on all pages
- [ ] Figures numbered and captioned
- [ ] File size under 50MB

## Part F: Test Docker Setup on Fresh System

**Simulate fresh installation:**

```bash
# Stop and remove everything
docker-compose down -v
docker system prune -a -f

# Remove databases
rm vulnerable/database/valves.db
rm patched/database/valves.db

# Re-initialize
cd vulnerable
python3 init_db.py
python3 populate_db.py
cd ../patched
python3 init_db.py
python3 populate_db.py
cd ..

# Test clean build
docker-compose up --build

# Verify:
# 1. Both apps start without errors
# 2. Can access http://localhost:5001 and :5002
# 3. Can login with credentials
# 4. Dashboard shows 150 valves
# 5. All pages load
```

**If successful, your Docker setup is verified ✓**

## Part G: Create Submission Archive

### Option 1: ZIP Archive (Recommended)

```bash
cd /Users/azuolasbalbieris/Documents/Academic/Cybersecurity/task_5_CS437

# Create zip (excluding unnecessary files)
zip -r CS437_Task5_TeamX.zip submission_package/ \
  -x "*.pyc" "*.DS_Store" "*__pycache__/*" "*venv/*" "*.git/*" \
  -x "*/uploads/firmware/*" "*/uploads/configs/*" "*/uploads/encrypted/*"

# Verify size
ls -lh CS437_Task5_TeamX.zip

# Expected size: 5-20 MB (without venv and uploads)
```

### Option 2: TAR.GZ Archive

```bash
tar -czf CS437_Task5_TeamX.tar.gz \
  --exclude='*.pyc' \
  --exclude='*__pycache__*' \
  --exclude='*venv*' \
  --exclude='*.DS_Store' \
  --exclude='*/uploads/firmware/*' \
  --exclude='*/uploads/configs/*' \
  --exclude='*/uploads/encrypted/*' \
  submission_package/

ls -lh CS437_Task5_TeamX.tar.gz
```

### Test Archive

```bash
# Create test directory
mkdir -p /tmp/test_extraction
cd /tmp/test_extraction

# Extract
unzip /Users/azuolasbalbieris/Documents/Academic/Cybersecurity/task_5_CS437/CS437_Task5_TeamX.zip

# Verify structure
ls -la submission_package/
ls -la submission_package/vulnerable/
ls -la submission_package/patched/

# Try to run
cd submission_package
docker-compose up --build

# If it works, archive is good! ✓
```

## Part H: Upload and Submit

### Submission Methods

**Check assignment instructions for specific submission method:**

**Option 1: Email Submission**
```
To: [instructor email]
Cc: [TA emails]
Subject: CS437 Task 5 Submission - Team X

Dear Professor [Name],

Please find attached our CS 437 Task 5 submission.

Team Members:
- [Name 1] - [ID]
- [Name 2] - [ID]
- [Name 3] - [ID]

Submission includes:
- Source code (vulnerable + patched)
- Docker configuration
- Database with 150 records
- Population scripts
- Report (PDF, 35 pages)
- Video demonstration link

Video Link: [URL]

If you have any questions, please contact us at [email].

Best regards,
Team X
```

**Attachments:**
- CS437_Task5_TeamX.zip (or upload to Drive and share link if too large)
- REPORT.pdf (if separate)

**Option 2: LMS Upload**
1. Login to course LMS
2. Navigate to assignment submission
3. Upload CS437_Task5_TeamX.zip
4. Paste video link in comments/description
5. Submit

**Option 3: Google Drive/OneDrive Submission**
1. Upload CS437_Task5_TeamX.zip to Drive
2. Set sharing to "Anyone with link can view"
3. Copy link
4. Submit link via email/LMS

## Part I: Pre-Submission Verification

### Final Team Review Meeting (1-2 hours)

**Agenda:**

**1. Document Review (30 min)**
- Open README.md - verify all info correct
- Open REPORT.pdf - quick scan through
- Open VIDEO_LINK.txt - test video plays
- Verify team member names/IDs correct everywhere

**2. Code Review (20 min)**
- Check vulnerable/app/routes/upload.py - vulnerabilities present
- Check patched/app/routes/upload.py - vulnerabilities fixed
- Check vulnerable/app/routes/valves.py - SQL injection present
- Check patched/app/routes/valves.py - SQL injection fixed
- Verify no debugging code left in
- Verify no commented-out code

**3. Docker Test (20 min)**
- Fresh docker-compose up
- Test login on both versions
- Upload a file on vulnerable (should work)
- Upload same file on patched (should fail)
- Test SQL injection on vulnerable as admin (should work)
- Test SQL injection on patched (should fail)
- Check monitoring dashboard (should show attacks)

**4. Database Verification (5 min)**
```bash
sqlite3 vulnerable/database/valves.db "SELECT COUNT(*) FROM valves;"
# Must output: 150

sqlite3 vulnerable/database/valves.db "SELECT COUNT(*) FROM users;"
# Must output: 4

sqlite3 patched/database/valves.db "SELECT COUNT(*) FROM valves;"
# Must output: 150
```

**5. Archive Test (10 min)**
- Extract archive in new folder
- Read README.md
- Run docker-compose up
- Verify it works from scratch

**6. Video Test (5 min)**
- Open video link
- Verify it plays
- Check volume audible
- Verify all team members appear/mentioned
- Confirm length 12-15 minutes

**7. Report Quality Check (10 min)**
- Page count: 30-40 pages ✓
- All screenshots visible ✓
- Table of contents works ✓
- No [TODO] or [INSERT HERE] markers ✓
- All sections complete ✓

### The Ultimate Checklist

```bash
cat > submission_package/SUBMISSION_CHECKLIST.md << 'EOF'
# Final Submission Checklist - CS437 Task 5

## Core Deliverables
- [ ] Vulnerable source code (complete, working)
- [ ] Patched source code (complete, working)
- [ ] docker-compose.yml (tested, working)
- [ ] Both Dockerfiles (tested, working)
- [ ] Database files (150+ records in valves table)
- [ ] populate_db.py script
- [ ] init_db.py script
- [ ] requirements.txt (both versions)
- [ ] REPORT.pdf (30-40 pages)
- [ ] VIDEO_LINK.txt with accessible video link

## Documentation
- [ ] README.md (comprehensive)
- [ ] STARTUP_GUIDE.md
- [ ] ARCHITECTURE.md
- [ ] VERSION.txt in both versions

## Vulnerabilities Verified
- [ ] CWE-434 Scenario 1 implemented and working
- [ ] CWE-434 Scenario 2 implemented and working
- [ ] CWE-434 Scenario 3 implemented and working
- [ ] SQL Injection implemented and working
- [ ] All vulnerabilities on separate pages/endpoints

## Patches Verified
- [ ] Scenario 1 patched and verified
- [ ] Scenario 2 patched and verified
- [ ] Scenario 3 patched and verified
- [ ] SQL Injection patched and verified
- [ ] All patches block attacks 100%

## Monitoring System
- [ ] Present in vulnerable version
- [ ] Present in patched version
- [ ] Logs all attack attempts
- [ ] Correct attack classification
- [ ] Shows allowed vs blocked correctly

## Testing Evidence
- [ ] Burp Suite screenshots included
- [ ] sqlmap outputs included
- [ ] Manual testing documented
- [ ] Monitoring screenshots included
- [ ] All tests passed on vulnerable
- [ ] All tests blocked on patched

## Report Quality
- [ ] 30-40 pages
- [ ] Professional formatting
- [ ] All 4 vulnerabilities documented (5-6 pages each)
- [ ] Tool usage explained
- [ ] Screenshots embedded and annotated
- [ ] Code snippets included (vulnerable vs patched)
- [ ] No spelling/grammar errors
- [ ] Table of contents
- [ ] Page numbers
- [ ] References section

## Video Quality
- [ ] 12-15 minutes length
- [ ] 1920x1080 resolution
- [ ] Audio clear
- [ ] All 4 vulnerabilities demonstrated
- [ ] Burp Suite shown
- [ ] sqlmap shown
- [ ] Monitoring shown
- [ ] Patched version shown
- [ ] Code comparison shown
- [ ] Team introduction
- [ ] Professional conclusion
- [ ] Uploaded and accessible

## Deployment
- [ ] Docker setup tested from scratch
- [ ] Both versions start without errors
- [ ] Both versions accessible on correct ports
- [ ] Login works (all users)
- [ ] Database populated correctly
- [ ] All features working

## Archive
- [ ] ZIP/TAR created
- [ ] Reasonable file size (<100MB)
- [ ] Extraction tested
- [ ] All files present
- [ ] No unnecessary files (venv, __pycache__, .DS_Store)
- [ ] README.md in root

## Team Information
- [ ] All team member names correct
- [ ] All student IDs correct
- [ ] All emails correct
- [ ] Task number correct (Task 5)
- [ ] Submission date correct

## Final Checks
- [ ] Video link tested in incognito/private window
- [ ] Video link works on mobile
- [ ] PDF opens in Adobe Reader
- [ ] PDF file size reasonable (<50MB)
- [ ] Archive extracts without errors
- [ ] All team members reviewed submission
- [ ] Contact information included
- [ ] Submission method confirmed
- [ ] Deadline verified
- [ ] Backup copy saved

## Pre-Submission Test
- [ ] Extracted archive in fresh directory
- [ ] Ran docker-compose up --build
- [ ] Both apps started successfully
- [ ] Tested one vulnerability (worked)
- [ ] Tested same on patched (blocked)
- [ ] Confirmed monitoring logged it
- [ ] Report PDF readable
- [ ] Video playable

## Submit When
- [ ] All above items checked ✓
- [ ] Team members approve
- [ ] Before deadline
- [ ] Confirmation received

---

**Signed:**
- [ ] [Name 1] - Reviewed and approved - Date: _____
- [ ] [Name 2] - Reviewed and approved - Date: _____
- [ ] [Name 3] - Reviewed and approved - Date: _____

**Submission Timestamp:** _____________________

**Submission Method:** _____________________

**Confirmation #:** _____________________
EOF

cat submission_package/SUBMISSION_CHECKLIST.md
```

## Part J: Post-Submission

### Keep Copies

```bash
# Backup submission to multiple locations

# External drive
cp CS437_Task5_TeamX.zip /Volumes/ExternalDrive/

# Cloud backup
# Upload to personal Google Drive/Dropbox

# Keep original project
# Don't delete task_5_CS437/ folder for at least 6 months
```

### Prepare for Demonstration Session

The assignment mentions a Zoom demonstration session.

**Prepare:**
1. Test Zoom beforehand
2. All team members must attend
3. Have application running
4. Be ready to demo live
5. Prepare to answer questions about:
   - Your design choices
   - Why vulnerabilities are realistic
   - How patches work
   - Testing methodology
   - OT security implications

**Practice Q&A:**
- "Why did you implement it this way?"
- "How does this relate to real SCADA systems?"
- "What if attacker tries [alternative attack]?"
- "Explain your testing methodology"
- "What did you learn from this project?"

## Part K: Troubleshooting Submission Issues

**"File too large for email (>25MB)":**
- Upload to Google Drive/OneDrive
- Share link with instructor
- Or split into parts (use split command)

**"Can't access video link":**
- Verify link is not set to "Private"
- Should be "Unlisted" (YouTube) or "Anyone with link" (Drive)
- Test link in incognito window

**"Docker build fails on instructor's machine":**
- Ensure requirements.txt is correct
- Ensure Dockerfile doesn't depend on local files
- Test on clean Docker installation

**"Report PDF has rendering issues":**
- Re-export with different settings
- Try "Save as PDF" instead of "Export as PDF"
- Reduce image quality if needed

**"Archive won't extract":**
- Verify ZIP/TAR is not corrupted (md5sum)
- Try creating with different tool
- Don't use special characters in filenames

## Summary Timeline

**Days Before Submission:**

**Day -3:**
- Finalize report
- Finish video editing
- Upload video

**Day -2:**
- Create submission package
- Test Docker from scratch
- Review everything as team

**Day -1:**
- Create archive
- Test archive extraction
- Fill out checklist
- Prepare backup submission method

**Submission Day:**
- Final verification (1 hour before deadline)
- Submit main package
- Verify submission received
- Celebrate! 🎉

## Final Notes

**Remember:**
- Submit BEFORE deadline (don't wait until last minute)
- Keep backups of everything
- Verify video link works for others
- Test Docker setup one more time
- All team members should review final package
- Keep project files for demonstration session

**You've worked hard on this project. Make sure the submission reflects that!**

---

## Congratulations!

You've completed:
- ✅ Implementation (4 vulnerabilities + patches)
- ✅ Testing (Burp Suite, sqlmap, manual)
- ✅ Documentation (30-40 page report)
- ✅ Demonstration (12-15 minute video)
- ✅ Packaging (complete submission package)

**Your CS 437 Task 5 assignment is complete!**

Good luck with the demonstration session and final grading!

---

**End of Step-by-Step Guide**

For questions during submission process, contact team members:
- [Name 1]: [Email]
- [Name 2]: [Email]
- [Name 3]: [Email]
