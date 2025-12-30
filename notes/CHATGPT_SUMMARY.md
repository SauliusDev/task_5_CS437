Got it. Let’s unpack exactly what you’re expected to build for Task 5 (Remote Valve Management System), what “vulnerable vs patched” really means, what the three CWE-434 variants are, what the role-based SQLi is, and how to design the monitoring/attack dashboard + Docker + report + video so it cleanly matches the rubric.

⸻

1) What the assignment is really asking for (in plain terms)

You are building two web apps (same features, different security posture):

A) Vulnerable version (intentionally insecure)

A SCADA-like web interface that:
	•	shows valve state (open/close %), last command time, comms status
	•	lets you issue commands (open/close), schedule operations, force resync
	•	generates logs (command exec, failed response, timeouts)
	•	has specific vulnerabilities (Task 5 list) that you can demonstrate exploiting with pentesting tools

B) Patched version (secure)

Same UI/features, but you:
	•	fix each vulnerability properly
	•	re-test to show exploitation no longer works

Hard constraints from rubric (non-negotiable)
	•	Each vulnerability on a separate page
	•	DB must have ≥ 100 records (include population script; include DB if possible)
	•	Dockerized vulnerable + patched
	•	Monitoring system page for both versions:
	•	logs each vuln/attack/access point
	•	shows request details
	•	classifies attacks (e.g., “SQLi attempt”, “Dangerous upload”, “Bypass: size limit”, etc.)
	•	Report must show:
	•	vulnerable code parts
	•	exploitation steps (with tools)
	•	patched code parts
	•	verification tests after patch
	•	Video must show:
	•	exploit demo
	•	patch demo
	•	testing tools used
	•	No forced/illogical vulns (e.g., don’t put OS command injection on login)

⸻

2) Task 5: what you must implement (exactly)

You have two vulnerability families:

(A) File upload vulnerabilities (CWE-434) — THREE distinct cases

You need three separate upload pages, each demonstrating a different situation:

1) “Classic CWE-434 with lack of protection”

Meaning: upload endpoint accepts dangerous files with basically no checks.

Typical SCADA-themed “reason”:
	•	“Upload valve configuration / firmware / schedule file”
But implemented insecurely: you allow upload of files that can be executed or served.

Operational impact you should show:
	•	attacker uploads something that leads to unauthorized behavior (e.g., server-side code execution if stack allows, or stored malicious content if files are served back)

2) “CWE-434 with lack of protection (2 insufficient protection mechanisms at the same time)”

This is very specific: you must implement two protections that look “secure” but are bypassable, and one must be file size.

So for example:
	•	protection #1: size limit (e.g., reject files > 1MB)
	•	protection #2: extension allowlist or naive MIME check (e.g., allow .jpg and .txt)

But both are implemented badly (bypassable).
You must be able to show bypass in demo.

3) “File scanning pipeline bypass via encryption”

This models a real-world OT mistake: security control exists, but it scans only plaintext.

Flow you build:
	•	server “scans” uploaded content (e.g., checks for signatures / forbidden strings / patterns)
	•	but scanning is done before decryption OR only if file is plaintext
	•	attacker uploads encrypted blob
	•	system later decrypts and processes it
	•	malicious payload bypasses scanning

This is not about cracking encryption — it’s about a pipeline design flaw:

“We scanned the file, but we scanned the wrong representation at the wrong time.”

⸻

(B) SQL Injection: “Conditional escaping based on user role”

You must implement the same input field/page, but:
	•	Admin input is not escaped
	•	User input is escaped
	•	SQLi is exploitable only when logged in as admin
	•	therefore low-privilege testing misses it

This is a classic “it passed QA because they tested as user”.

SCADA-themed example:
	•	A “log search” page or “valve command history filter” page
	•	Users can search logs by keyword / valve id / status
	•	App builds SQL query differently depending on role (bad idea), introducing SQLi only for admins.

⸻

3) What “each vulnerability must be on a separate page” means in practice

A clean layout:
	•	/vuln/upload1 → Classic unprotected upload
	•	/vuln/upload2 → Two bypassable controls (size + another weak mechanism)
	•	/vuln/upload3 → Encrypted scanning pipeline bypass
	•	/vuln/sqli-role → Role-based conditional escaping SQLi
	•	/monitor → Monitoring dashboard (works in both vulnerable + patched versions)

And your main SCADA pages:
	•	/dashboard (valves overview)
	•	/valves/:id (control panel: open/close/schedule/resync)
	•	/logs (view logs)
	•	/auth/login (roles: admin vs operator/user)

⸻

4) How to make the vulnerabilities “logical” for SCADA

You’ll be graded on realism. Here are logical story reasons:

Upload pages (logical in OT)
	•	“Upload valve operation schedule” (CSV/JSON)
	•	“Upload configuration bundle for valve network”
	•	“Upload firmware update package”
	•	“Upload diagnostic package / trace logs”

SQLi page (logical)
	•	“Search command execution logs”
	•	“Filter failed response logs”
	•	“Query timeout events by valve/site”

This makes sense in OT.

⸻

5) Monitoring system: what it should do (minimum that passes)

Think of it as a mini SIEM page inside your app.

What you must capture

For every request to:
	•	the upload endpoints
	•	the SQLi endpoint
	•	auth/login (since it’s an access point)
	•	valve control endpoints (open/close/schedule/resync)

Log:
	•	timestamp
	•	endpoint
	•	method
	•	user + role
	•	source IP (or dummy if localhost)
	•	user agent
	•	request parameters (sanitized in patched version)
	•	outcome (allowed/blocked/error)
	•	attack classification (if detected)

Attack classification examples
	•	UPLOAD_DANGEROUS_TYPE
	•	UPLOAD_BYPASS_EXTENSION
	•	UPLOAD_BYPASS_SIZE_LIMIT
	•	UPLOAD_ENCRYPTED_BYPASS_SCAN
	•	SQLI_PATTERN_DETECTED
	•	SQLI_SUCCESS_INDICATOR (e.g., abnormal query result size)
	•	AUTH_BRUTE_FORCE_SUSPECTED (optional)

Monitoring UI views
	•	A table of events with filters:
	•	by endpoint
	•	by classification
	•	by role
	•	by time range
	•	Clicking an event shows details (request metadata + why classified)

Important detail:
In the patched version, you should show that the same attacks are either:
	•	blocked (403 / validation error), OR
	•	neutralized (safe query, safe file handling)

and that the monitor page clearly shows blocked=true or similar.

⸻

6) What “patched version” should look like (conceptually)

You’ll want to show real fixes, not “blacklist” hacks.

Patching CWE-434 (upload)

Real-world defenses you can mention & implement:
	•	Store uploads outside web root (can’t be executed/served directly)
	•	Generate random filenames; never trust user filename
	•	Allowlist extensions and verify content type properly (magic bytes / file signature)
	•	Enforce size limit server-side (and possibly reverse proxy too)
	•	Virus/malware scanning (even a simplified “scanner” for the assignment)
	•	For the encryption pipeline: scan after decryption (or forbid encrypted uploads, or require scanning service that can handle archives/encrypted formats with policy)

Patching SQLi
	•	Always parameterized queries (prepared statements)
	•	No string concatenation
	•	Same code path regardless of role (role affects authorization, not escaping)
	•	Least privilege DB user (optional but good in report)
	•	Add server-side input validation (but validation alone is not the fix)

⸻

7) Tooling you’ll likely use in the demos (what each is for)

Burp Suite / OWASP ZAP
	•	Intercept requests, modify parameters, replay attacks
	•	Great for demonstrating:
	•	upload bypass attempts
	•	SQLi payload injection attempts
	•	role-based behavior differences

sqlmap
	•	Automated SQLi testing
	•	Perfect for your “missed during low-priv testing” storyline:
	1.	run as normal user → “not vulnerable”
	2.	run as admin → “vulnerable”
	•	In patched version: sqlmap fails

Postman
	•	Nice for clean demo of control endpoints:
	•	schedule valve op
	•	resync
	•	upload endpoints with different file bodies

Nikto / Nuclei (optional)
	•	Quick web misconfig scanning
	•	Not required, but looks good if it finds something in vulnerable and not in patched

⸻

8) Docker expectations (what “dockerized” usually means)

You should have something like:
	•	docker-compose.vuln.yml
	•	docker-compose.patched.yml

Each spins up:
	•	web app container
	•	database container (MySQL/Postgres) OR SQLite inside container

Because rubric requires 100+ records, it’s easiest if:
	•	DB container runs init scripts on startup
	•	you include seed.sql / seed.py

Tip: Use the same dataset for both vuln and patched, so results are comparable.

⸻

9) Report structure that matches the rubric (copy/paste outline)
	1.	Introduction
	•	SCADA scenario description
	•	architecture diagram (simple)
	2.	Environment
	•	tech stack
	•	Docker setup instructions
	•	credentials for demo users (admin/operator)
	3.	System Features
	•	valve dashboard
	•	commands
	•	scheduling
	•	logs
	4.	Vulnerabilities (one section per page)
For each vuln page:
	•	Vulnerability description (CWE link/name)
	•	Where it exists (endpoint + code snippet)
	•	Why it is vulnerable (root cause)
	•	Exploitation steps
	•	tool used (Burp/sqlmap/etc.)
	•	request examples
	•	screenshots
	•	Operational impact (what changed in SCADA)
	5.	Monitoring system
	•	what it logs
	•	detection logic (classification rules)
	•	screenshots
	6.	Patches
For each vuln:
	•	what you changed
	•	why it fixes it
	•	re-test evidence (tool output + screenshots)
	7.	Conclusion
	•	lessons learned / OT relevance

⸻

10) What your demo video should show (clean storyline)

For each vulnerability:
	1.	show normal behavior
	2.	show exploit (tool + result)
	3.	show monitoring entry created
	4.	switch to patched version
	5.	repeat attack
	6.	show it fails + monitoring marks it blocked

For SQLi specifically, emphasize:
	•	user role test fails to detect
	•	admin role test succeeds
	•	patched version fixes for all roles

⸻

11) How I can help you going forward (what you said you want)

You said: “I will ask questions about all the tools, concepts, etc.”

Perfect. I can help in these modes:
	•	explain any concept simply (CWE-434, SQLi, scanning pipelines, OT impact)
	•	help you design the pages so they satisfy rubric
	•	help you plan demos with Burp/sqlmap/ZAP/Postman
	•	help you write the report sections and the monitoring classification rules
	•	help you build a “checklist” so you don’t miss rubric requirements

⸻

If you want a good next step: tell me what stack you’re using (Flask/Node/Spring/etc.) and which DB (SQLite vs Postgres/MySQL). Then I’ll map Task 5 into a concrete folder structure + endpoints + page list + what to demo with each tool, in a way that’s easy to split among 3 group members.