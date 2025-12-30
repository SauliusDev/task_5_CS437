Perfect — this is exactly the right moment to use Cursor 👍
What you need now is not code, but a clear master prompt + roadmap that you can iteratively feed to Cursor without losing control.

Below I’ll give you:
	1.	Mental model of the assignment (so you don’t get lost)
	2.	One master roadmap (phases)
	3.	Exact Cursor prompting strategy
	4.	A ready-to-use “starter prompt” for Cursor
	5.	Rules for working with Cursor safely

No fluff — this is how people actually survive large security assignments.

⸻

1️⃣ Mental model (lock this in)

You are building TWO versions of the SAME app:

Remote Valve Management System
│
├── Vulnerable Version  ❌
│   ├── Realistic OT-style bugs
│   ├── Exploitable with Burp / sqlmap
│   └── Logs attacks
│
└── Patched Version ✅
    ├── Same features
    ├── Secure coding
    └── Attacks no longer work

Everything else (Docker, report, demo) is supporting material.

If at any point you ask:

“Is this helping demonstrate a vulnerability or a patch?”

If the answer is no → don’t do it.

⸻

2️⃣ The full roadmap (this is what Cursor must follow)

PHASE 0 – Architecture & constraints (NO code yet)

Goal: Decide what exists before writing anything.
	•	Web app (Flask)
	•	Database (SQLite or MySQL)
	•	Users:
	•	admin
	•	operator
	•	Valves table (100+ records)
	•	Logs table
	•	Upload directory
	•	Monitoring dashboard

👉 Output: design + schema

⸻

PHASE 1 – SAFE BASELINE APPLICATION

Goal: Build a working SCADA interface with NO vulnerabilities.

Features:
	•	Login
	•	View valves
	•	Open/close valves
	•	Schedule operations
	•	Upload config/firmware files (safe)
	•	View logs

⚠️ This version becomes your patched reference later.

⸻

PHASE 2 – CLONE → VULNERABLE VERSION

Goal: Same app, but now you intentionally weaken it.

You do NOT redesign the app — you break it.

⸻

PHASE 3 – Implement REQUIRED vulnerabilities

A) CWE-434 (3 upload scenarios)
	1.	No validation at all
	2.	Two weak protections:
	•	size limit
	•	blacklist / MIME check
	3.	Encrypted upload bypass:
	•	scan plaintext only
	•	decrypt later

Each on separate pages / endpoints.

⸻

B) SQL Injection (role-based escaping)
	•	Same input field
	•	User → escaped
	•	Admin → raw SQL
	•	Exploitable only as admin

⸻

PHASE 4 – Monitoring system

Goal: Prove you can observe attacks.
	•	Middleware logging
	•	Attack classification:
	•	file upload abuse
	•	SQL injection
	•	size bypass
	•	encrypted payload
	•	Dashboard page

⸻

PHASE 5 – PATCHED VERSION

Goal: Fix everything correctly.
	•	Allow-list uploads
	•	Size + MIME + content checks
	•	Decrypt → scan → store
	•	SQL parameterized queries
	•	Role-independent escaping
	•	CSRF protection (bonus but good)

⸻

PHASE 6 – Docker

Goal: Make it runnable anywhere.
	•	Dockerfile (vulnerable)
	•	Dockerfile (patched)
	•	DB seed script
	•	Exposed ports

⸻

PHASE 7 – Testing & demo

Goal: Evidence.
	•	Burp interception
	•	sqlmap exploitation
	•	Upload bypass demo
	•	Logs proving attacks
	•	Patched version blocking

⸻

PHASE 8 – Report & video

Goal: Explain, not impress.
	•	Before / after code
	•	Payloads
	•	Screenshots
	•	Tool output

⸻

3️⃣ How to use Cursor correctly (VERY IMPORTANT)

Cursor is powerful only if you control scope.

❌ What NOT to do
	•	“Build me the whole project”
	•	“Add vulnerabilities” (too vague)
	•	Let it design security for you

✅ What TO do
	•	One phase at a time
	•	Explicitly say:
	•	vulnerable OR patched
	•	insecure ON PURPOSE
	•	no extra features

⸻

4️⃣ Your FIRST Cursor prompt (copy-paste this)

Use this exactly as written 👇

You are helping me with a university cybersecurity assignment.

Goal:
Design (NOT implement yet) a Dockerized Flask-based "Remote Valve Management System" SCADA-style web application.

Important constraints:
- This is an OT / SCADA demo, not a real industrial system
- The project will have TWO versions: vulnerable and patched
- Vulnerabilities will be intentionally introduced later
- For now, design a SAFE baseline architecture

What I need in this step:
1) High-level system architecture (components)
2) Database schema (tables, fields, relationships)
3) List of REST endpoints with purpose
4) Description of user roles (admin vs operator)
5) File upload workflow (safe version)
6) Logging strategy (what events are logged)

Do NOT:
- Write actual Flask code yet
- Add vulnerabilities yet
- Overengineer frontend

Output format:
- Clear sections
- Bullet points
- Simple explanations

Let Cursor answer this.

⸻

5️⃣ How you iterate after that

Then you proceed step by step.

Example follow-ups:

Phase 1

Now implement the SAFE baseline Flask application using the architecture above.
Requirements:
- Flask
- SQLite
- Basic HTML templates
- No vulnerabilities
- Clean, readable code

Phase 3 – Vulnerabilities

Now modify ONLY the vulnerable version to introduce CWE-434 unrestricted file upload.
This must be intentionally insecure and realistic.
Explain in comments why it is vulnerable.

SQLi

Introduce SQL injection by conditionally escaping user input based on role.
Admin input must be unescaped.
User input must be escaped.
Use the same input field.

Patching

Now refactor this code into a patched version.
Use parameterized queries and proper file validation.
Explain in comments why this is secure.


⸻

6️⃣ Golden rules (this saves projects)
	1.	One vulnerability = one endpoint
	2.	Never mix vulnerable & patched code
	3.	Comment WHY it’s vulnerable
	4.	If Burp/sqlmap can’t exploit it → it’s wrong
	5.	Monitoring logs must prove the attack

⸻

7️⃣ You are doing this the RIGHT way

This assignment looks scary because:
	•	OT + SCADA + Security + Docker

But in reality it’s:

A web app with deliberately bad decisions

You already have the mindset to finish this cleanly.

⸻

Next step (tell me which one)
	•	“Help me review Cursor’s architecture output”
	•	“Help me define the DB schema myself”
	•	“Help me design the upload vulnerabilities precisely”

We’ll go phase by phase until submission-ready.

