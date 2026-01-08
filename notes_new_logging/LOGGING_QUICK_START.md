# Enhanced Logging System - Quick Start Guide

## Installation & Setup

### For New Installation

```bash
cd patched  # or vulnerable
python init_db.py
python populate_db.py
python run.py
```

### For Existing Database

```bash
cd patched  # or vulnerable
python migrate_database.py
python run.py
```

## Accessing the Monitoring Dashboard

1. Navigate to `http://localhost:5001/monitoring` (patched) or `http://localhost:5000/monitoring` (vulnerable)
2. Login as admin (default: admin/admin)
3. Explore the 5 main tabs

## Key Features

### 1. Overview Tab
- Real-time attack statistics
- Attack type distribution
- High-risk alerts
- Quick status overview

### 2. Attack Logs Tab
- Complete attack history
- Filterable by type/risk/time
- Detailed attack information
- Raw request data viewing

### 3. Actionable Tab
- Attacks requiring immediate attention
- Recommended actions
- Quick-action buttons
- One-click IP blocking

### 4. Action Center Tab
- Manage blocked IPs
- Manage locked accounts
- View security action history
- Reverse actions
- Manual block/lock interface

### 5. Auto-Response Rules Tab
- View automated rules
- Enable/disable rules
- Monitor thresholds
- Configure responses

## Common Tasks

### Block an IP Address

**Via Dashboard:**
1. Go to Action Center tab
2. Click "Block New IP"
3. Enter IP, reason, and duration
4. Click "Block IP"

**Via API:**
```bash
curl -X POST http://localhost:5001/api/security/block-ip \
  -H "Content-Type: application/json" \
  -d '{"ip_address": "192.168.1.100", "reason": "Manual block", "duration_hours": 24}'
```

### Unblock an IP Address

**Via Dashboard:**
1. Go to Action Center tab
2. Find IP in Blocked IPs table
3. Click "Unblock" button

### Lock a User Account

**Via API:**
```bash
curl -X POST http://localhost:5001/api/security/lock-account \
  -H "Content-Type: application/json" \
  -d '{"user_id": 2, "reason": "Suspicious activity", "duration_hours": 2}'
```

### View Attack Details

**Via Dashboard:**
1. Go to Attack Logs tab
2. Click "View" button on any attack
3. Modal shows complete details including:
   - Attack metadata
   - Risk score and classification
   - Recommended action
   - Reverse action steps
   - Raw request data

### Reverse a Security Action

**Via Dashboard:**
1. Go to Action Center tab
2. Scroll to Recent Security Actions
3. Find action to reverse
4. Click "Reverse" button

### Configure Auto-Response Rules

**Via Dashboard:**
1. Go to Auto-Response Rules tab
2. Click "Toggle" to enable/disable rule
3. Rules automatically apply when enabled

## Testing Attack Detection

### Test Login Brute Force
```bash
# Make 5+ failed login attempts
for i in {1..6}; do
  curl -X POST http://localhost:5001/login \
    -d "username=admin&password=wrong"
done
# Check monitoring dashboard - attack logged and IP blocked
```

### Test SQL Injection
```bash
# Try SQL injection in search
curl -X POST http://localhost:5001/valves/search \
  -d "search=' OR '1'='1"
# Check monitoring dashboard - attack logged and blocked
```

### Test Directory Brute Force
```bash
# Access many non-existent paths
for i in {1..25}; do
  curl http://localhost:5001/nonexistent$i
done
# Check monitoring dashboard - brute force detected
```

### Test Rate Limiting
```bash
# Send 100+ requests rapidly
for i in {1..105}; do
  curl http://localhost:5001/ &
done
# Check monitoring dashboard - rate limit violation logged
```

## API Endpoints Reference

### Security Actions
- `POST /api/security/block-ip` - Block IP
- `POST /api/security/unblock-ip` - Unblock IP
- `POST /api/security/lock-account` - Lock account
- `POST /api/security/unlock-account` - Unlock account
- `POST /api/security/clear-sessions` - Clear sessions
- `GET /api/security/blocked-ips` - List blocked IPs
- `GET /api/security/locked-accounts` - List locked accounts
- `GET /api/security/actions-history` - Action history
- `POST /api/security/reverse-action/<id>` - Reverse action
- `GET /api/security/auto-response-rules` - List rules
- `POST /api/security/configure-auto-response` - Configure rules
- `GET /api/security/attack-details/<id>` - Attack details

### Monitoring
- `GET /api/monitoring/stats` - Get statistics
- `GET /api/monitoring/attacks` - Get attacks
  - `?type=sql_injection` - Filter by type
  - `?risk_threshold=70` - Filter by risk
  - `?limit=100` - Limit results
- `GET /api/monitoring/actionable` - Get actionable attacks

## Default Auto-Response Rules

1. **Auto-block brute force**
   - Trigger: 5 failed login attempts in 10 minutes
   - Action: Block IP for 24 hours

2. **Auto-block SQL injection**
   - Trigger: 3 SQL injection attacks in 60 minutes
   - Action: Block IP for 24 hours

3. **Auto-lock compromised account**
   - Trigger: 5 failed logins per user in 15 minutes
   - Action: Lock account for 2 hours

4. **Rate limit violators**
   - Trigger: 100 requests per minute
   - Action: Block IP for 30 minutes

5. **Block privilege escalation**
   - Trigger: 1 privilege escalation attempt in 60 minutes
   - Action: Block IP for 24 hours

## Log Entry Format

Each attack log includes:
- **Metadata**: Timestamp, IP, user agent, endpoint, method, payload
- **Classification**: Type, category, severity, risk score
- **Action**: Recommended, taken, reversible, reverse steps

## Troubleshooting

### "Database already exists" error
```bash
# Remove old database and reinitialize
rm database/valves.db
python init_db.py
python populate_db.py
```

### "No module named 'app'" error
```bash
# Make sure you're in the correct directory
cd patched  # or vulnerable
python run.py
```

### Can't access monitoring dashboard
```bash
# Make sure you're logged in as admin
# Default credentials: admin/admin
```

### Auto-response not working
1. Check rule is enabled in Auto-Response Rules tab
2. Verify threshold has been reached
3. Check time window settings
4. Review Recent Security Actions for execution

## For Your Report/Video

### Key Demo Points

1. **Show comprehensive detection**
   - Trigger different attack types
   - Show them appearing in dashboard
   - Highlight metadata and classification

2. **Show risk-based prioritization**
   - Filter high-risk attacks
   - Show actionable attacks tab
   - Explain risk scoring

3. **Demonstrate manual actions**
   - Block an IP manually
   - Unblock it
   - Lock an account
   - Unlock it

4. **Demonstrate automated responses**
   - Trigger auto-block with failed logins
   - Show it in security actions with "Auto" flag
   - Show IP in blocked list

5. **Show action reversibility**
   - Reverse a block action
   - Show IP removed from blocked list
   - Explain audit trail

6. **Show detailed logging**
   - Open attack detail modal
   - Show all metadata fields
   - Highlight classification and recommended action
   - Show reverse action steps

## Support

For issues or questions:
1. Check LOGGING_SYSTEM_IMPLEMENTATION.md for detailed documentation
2. Review database schema in init_db.py
3. Check model methods in models.py
4. Review detection logic in utils/monitoring.py
