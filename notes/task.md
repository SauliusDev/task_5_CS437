
Assignment CS437
Completion requirements
Opened: Thursday, 18 December 2025, 12:00 AM
Due: Sunday, 4 January 2026, 11:59 PM
In this assignment, you are asked to implement vulnerable and patched projects that can demonstrate given vulnerabilities/misconfigurations and/or protection mechanisms. You will containerize your application using Docker and prepare a detailed report outlining how these vulnerabilities can be exploited, providing a hands-on approach to learning secure coding practices. 

In this assignment, you will be working in a group environment. Please note that each responsibility can only be taken by only 2 groups. Each group can only select one task. If a responsibility is already taken by 2 groups in the excel sheet, please pick another one. Each group must contain exactly 3 people. If you are unable to find one, you will be randomly assigned to a group.


Please register your task and group members here: 
Use your Sabancı University Account please, otherwise you won't be able see!
https://docs.google.com/spreadsheets/d/1muZTBIcd45bEav70tUVrTK-0fm_XV_8CwXtENQR4wU8/edit?usp=sharing
USE Sabancı University Account to get the link

CS 437 Assignment 2025 OT security.pdf CS 437 Assignment 2025 OT security.pdf18 December 2025, 2:51 PM

Assignment : Develop, Exploit, and Patch a Vulnerable SCADA Interfaces
Pick one task and register it to the given Google sheet, sheet can be found below. You
need 3 people.
Learning outcomes:
●
Design and implement a basic SCADA web interface
●
Identify and intentionally introduce security vulnerabilities in SCADA interfaces,
demonstrating an understanding of how insecure coding practices manifest in real-world
OT systems.
Analyze the attack surface of SCADA web applications, including authentication
mechanisms, data acquisition components, control endpoints, and third-party
integrations.
Exploit common web and OT-specific vulnerabilities
Demonstrate the operational impact of vulnerabilities by showing how successful
exploitation can affect process integrity, availability, and safety.
Apply penetration-testing tools and techniques (e.g., Burp Suite, sqlmap, custom
scripts) to systematically discover, validate, and exploit vulnerabilities in SCADA
interfaces.
Assess the limitations of naive or incorrect security controls, such as
blacklist-based filtering, manual input escaping, or trust in third-party data sources.
Implement secure coding countermeasures to remediate identified vulnerabilities,
including proper input validation, parameterized queries, authentication hardening,
CSRF protection, and secure file handling.
Patch and refactor vulnerable code while preserving system functionality and
operational requirements typical of OT environments.
Evaluate the effectiveness of applied security fixes through re-testing and
verification, demonstrating that vulnerabilities are no longer exploitable.
Document vulnerabilities, exploitation steps, and remediation actions using a
report.
●
●
●
●
●
●
Rules :
Each task can be only taken twice !
Your team must consist of 3 people.
Built a SCADA web application based on Scenario
Both vulnerable and patched versions are needed!
Report is needed explain your vulnerable parts and also patches
In your report, explanations must show the vulnerable parts also patched parts as well as how
exploitation has been done. Pentesting tools must be used to demonstrate the vulnerabilities
and patched versions.
Each SQL database should be populated with at least 100 records.
Also include population script and (if possible) database.
No Forced vulnerabilities: Make sure that vulnerability you are putting is logical, for instance OS
command injection should not be introduced in the login page.
Each group must develop a monitoring system for both vulnerable and patched systems:
The system should be able monitor each vulnerability, abuse,attack and access point. This page
should be able to display correct details of the request / attacks and present classification of the
attacks.
Each vulnerability must be on a separate page
What is needed in the submission:
1) Report
2) Vulnerable source codes and requirements
3) Patched version source codes and requirements
4) Dockerized version of vulnerable and patched version
5) Video explaining your application vulnerable version
a) How these vulnerabilities are exploited
b) How these vulnerabilities are patched
c) How these vulnerabilities are tested (Which tools and demonstration is needed!)
Do not forget there will be a demonstration session (zoom meeting) and all group
members must be present!

Task 5 :
Scenario: Remote Valve Management System
System: Field valve network
Interface shows:
Valve open/close percentage
Last command timestamp
Communication status
Logs generated:
Command execution logs
Failed valve response logs
Communication timeout logs
Capabilities:
Open/close valves
Schedule valve operations
Force re-synchronization
Vulnerabilities : CWE-434 Unrestricted Upload of File with Dangerous Type
->1st Classic CWE-434 with lack of protection
->2nd CWE- 434 with lack of protection (2 insufficient protection mechanism at the same time)
There must be 2 protection mechanisms which can be bypassed by the attacks
One of this must be size of the file
->3rd File scanning pipeline bypass via encryption
Server scans only plaintext; attacker uploads encrypted blob that’s decrypted later.
Student should be able demonstrate all this
SQL injection :
SQL injection Conditional Escaping Based on User Role (Same input area)
-Admin input not escaped, user input is
-SQLi only exploitable with higher privileges
-Missed during low-privilege testing
Patched version : Please also create a separated patched version and make sure to explain
all the patches.
Monitoring system:
The system should be able monitor each vulnerability, abuse,attack and access point. This
page should be able to display correct details of the request / attacks and present
classification of the attacks.
Testing : Pentesting tools must be used to demonstrate the vulnerabilities and patched
versions.
Some examples: Burp Suite, OWASP ZAP, SQLmap, XSStrike, Postman, Nuclei, Nikto