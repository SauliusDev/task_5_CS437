# Schedule Execution Test Guide

## Overview
Both vulnerable and patched versions now have **automatic schedule execution** enabled.

## What Was Added

### 1. APScheduler Dependency
- Added to `requirements.txt` in both versions
- Runs background jobs without blocking the main Flask app

### 2. Scheduler Module (`app/utils/scheduler.py`)
**Location**: 
- `vulnerable/app/utils/scheduler.py`
- `patched/app/utils/scheduler.py`

**Functionality**:
- Checks for pending schedules every **30 seconds**
- Executes commands when scheduled time arrives
- Updates valve states in database
- Creates command logs
- Marks schedules as 'executed' or 'failed'

### 3. Integration with Flask App
**Modified Files**:
- `vulnerable/app/app.py`
- `patched/app/app.py`

**Changes**:
```python
from app.utils.scheduler import start_scheduler, stop_scheduler
start_scheduler()  # Starts when app starts
atexit.register(stop_scheduler)  # Stops when app stops
```

## How to Test

### Step 1: Rebuild Docker Containers
```bash
cd /Users/azuolasbalbieris/Documents/Academic/Cybersecurity/task_5_CS437
docker-compose down
docker-compose up --build -d
```

### Step 2: Access the Application
- **Vulnerable**: http://localhost:5002
- **Patched**: http://localhost:5001

### Step 3: Create a Test Schedule

1. **Login** with:
   - Username: `admin`
   - Password: `admin123`

2. **Navigate to Schedules**:
   - Click "Schedules" in navigation bar

3. **Create New Schedule**:
   - Click "Create Schedule" button
   - Select a valve (e.g., "V-001")
   - Set scheduled time: **1 minute from now**
   - Choose command: "OPEN" or "CLOSE"
   - Click "Create Schedule"

### Step 4: Wait and Verify

**After ~1 minute** (scheduler runs every 30 seconds):

1. **Refresh Schedules Page**:
   - Status should change from "pending" to "executed"
   - "Executed At" timestamp should be filled

2. **Check Valve Status**:
   - Go to "Valves" page
   - Find the valve you scheduled
   - Verify:
     - Open percentage changed (100% for OPEN, 0% for CLOSE)
     - "Last Command" shows the executed command
     - "Last Command Timestamp" is recent

3. **Check Command Logs**:
   - Go to "Logs" → "Command Logs"
   - You should see a new entry for the scheduled command
   - Status should be "success" (90% chance)

## Scheduler Behavior

### Execution Window
```
Schedule Time: 12:00:00
Scheduler checks every 30 seconds

Timeline:
11:59:30 → Check (not yet time)
12:00:00 → Schedule time arrives
12:00:00 → Check (execute now!) ✓
12:00:30 → Already executed
```

### What Gets Executed

| Command | Action |
|---------|--------|
| **OPEN** | Sets valve to 100% open |
| **CLOSE** | Sets valve to 0% open |
| **ADJUST** | Sets valve to specified percentage |
| **SYNC** | Syncs to current valve state |

### Success/Failure Simulation
- **90% success rate** (simulates real hardware)
- **10% failure rate** with random errors:
  - "Connection timeout"
  - "Hardware error"
  - "Invalid response"

## Database Updates

When schedule executes successfully:

1. **schedules table**:
   ```sql
   status = 'executed'
   executed_at = current_timestamp
   ```

2. **valves table**:
   ```sql
   open_percentage = new_value
   last_command = command
   last_command_timestamp = current_timestamp
   updated_at = current_timestamp
   ```

3. **command_logs table**:
   ```sql
   New row inserted with execution details
   ```

## Monitoring Scheduler Activity

### View Docker Logs
```bash
# Vulnerable version
docker logs -f scada_vulnerable

# Patched version  
docker logs -f scada_patched
```

### What to Look For
You won't see explicit scheduler logs unless there's an error, but you'll notice:
- Database activity every 30 seconds
- Schedule status changes
- Command log entries appearing

## Testing Multiple Schedules

**Create several schedules**:
1. Schedule 1: Opens valve V-001 in 1 minute
2. Schedule 2: Closes valve V-002 in 2 minutes
3. Schedule 3: Adjusts valve V-003 to 50% in 3 minutes

**Watch them execute automatically!**

## Troubleshooting

### Schedules Not Executing?

1. **Check scheduler started**:
   ```bash
   docker logs scada_vulnerable 2>&1 | grep -i schedule
   ```

2. **Verify time format**:
   - Scheduled time must be in the future
   - Uses container timezone (UTC)

3. **Check database**:
   ```bash
   docker exec -it scada_vulnerable sqlite3 database/valves.db
   SELECT * FROM schedules WHERE status = 'pending';
   ```

### Failed Schedules?

This is normal! 10% of commands fail (simulates real hardware issues).
- Check `command_logs` table for error messages
- Schedule status will be 'failed' instead of 'executed'

## Stop Scheduler

The scheduler automatically stops when containers stop:

```bash
docker-compose down
```

## Summary

✅ **Schedules now work automatically**
✅ **Runs in both vulnerable and patched versions**
✅ **Checks every 30 seconds**
✅ **Updates database on execution**
✅ **Simulates real hardware behavior (90% success)**

The scheduler makes your SCADA system more realistic by actually executing scheduled valve operations!
