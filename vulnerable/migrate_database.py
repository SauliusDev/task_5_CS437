import sqlite3
import os
from datetime import datetime

DATABASE_PATH = 'database/valves.db'

def migrate_database():
    if not os.path.exists(DATABASE_PATH):
        print(f"Database not found at {DATABASE_PATH}")
        print("Please run init_db.py first to create a new database with the updated schema.")
        return
    
    backup_path = f'database/valves_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
    
    print(f"Creating backup at {backup_path}...")
    import shutil
    shutil.copy2(DATABASE_PATH, backup_path)
    print("Backup created successfully!")
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    print("Starting database migration...")
    
    try:
        print("Adding new columns to attack_logs table...")
        cursor.execute('ALTER TABLE attack_logs ADD COLUMN classification TEXT')
    except sqlite3.OperationalError:
        print("  - classification column already exists")
    
    try:
        cursor.execute('ALTER TABLE attack_logs ADD COLUMN recommended_action TEXT')
    except sqlite3.OperationalError:
        print("  - recommended_action column already exists")
    
    try:
        cursor.execute('ALTER TABLE attack_logs ADD COLUMN action_taken TEXT')
    except sqlite3.OperationalError:
        print("  - action_taken column already exists")
    
    try:
        cursor.execute('ALTER TABLE attack_logs ADD COLUMN action_reversible BOOLEAN DEFAULT 1')
    except sqlite3.OperationalError:
        print("  - action_reversible column already exists")
    
    try:
        cursor.execute('ALTER TABLE attack_logs ADD COLUMN reverse_action_steps TEXT')
    except sqlite3.OperationalError:
        print("  - reverse_action_steps column already exists")
    
    try:
        cursor.execute('ALTER TABLE attack_logs ADD COLUMN risk_score INTEGER DEFAULT 0')
    except sqlite3.OperationalError:
        print("  - risk_score column already exists")
    
    try:
        cursor.execute('ALTER TABLE attack_logs ADD COLUMN related_attack_id INTEGER')
    except sqlite3.OperationalError:
        print("  - related_attack_id column already exists")
    
    try:
        cursor.execute('ALTER TABLE attack_logs ADD COLUMN raw_request_data TEXT')
    except sqlite3.OperationalError:
        print("  - raw_request_data column already exists")
    
    try:
        cursor.execute('ALTER TABLE attack_logs ADD COLUMN response_status INTEGER')
    except sqlite3.OperationalError:
        print("  - response_status column already exists")
    
    try:
        cursor.execute('ALTER TABLE attack_logs ADD COLUMN geolocation TEXT')
    except sqlite3.OperationalError:
        print("  - geolocation column already exists")
    
    print("Creating new tables...")
    
    try:
        cursor.execute('''
            CREATE TABLE blocked_ips (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ip_address TEXT UNIQUE NOT NULL,
                reason TEXT NOT NULL,
                blocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                blocked_until TIMESTAMP,
                auto_unblock BOOLEAN DEFAULT 0,
                blocked_by_user_id INTEGER,
                attack_log_id INTEGER,
                is_active BOOLEAN DEFAULT 1,
                FOREIGN KEY (blocked_by_user_id) REFERENCES users(id),
                FOREIGN KEY (attack_log_id) REFERENCES attack_logs(id)
            )
        ''')
        print("  - blocked_ips table created")
    except sqlite3.OperationalError:
        print("  - blocked_ips table already exists")
    
    try:
        cursor.execute('''
            CREATE TABLE failed_login_attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                ip_address TEXT NOT NULL,
                attempt_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                user_agent TEXT,
                attack_log_id INTEGER,
                FOREIGN KEY (attack_log_id) REFERENCES attack_logs(id)
            )
        ''')
        print("  - failed_login_attempts table created")
    except sqlite3.OperationalError:
        print("  - failed_login_attempts table already exists")
    
    try:
        cursor.execute('''
            CREATE TABLE security_actions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action_type TEXT NOT NULL CHECK(action_type IN (
                    'block_ip',
                    'unblock_ip',
                    'lock_account',
                    'unlock_account',
                    'clear_sessions',
                    'delete_file',
                    'quarantine_file',
                    'alert_admin'
                )),
                target TEXT NOT NULL,
                reason TEXT NOT NULL,
                executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                executed_by INTEGER,
                reversed_at TIMESTAMP,
                reversed_by INTEGER,
                attack_log_id INTEGER,
                automated BOOLEAN DEFAULT 0,
                FOREIGN KEY (executed_by) REFERENCES users(id),
                FOREIGN KEY (reversed_by) REFERENCES users(id),
                FOREIGN KEY (attack_log_id) REFERENCES attack_logs(id)
            )
        ''')
        print("  - security_actions table created")
    except sqlite3.OperationalError:
        print("  - security_actions table already exists")
    
    try:
        cursor.execute('''
            CREATE TABLE auto_response_rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rule_name TEXT UNIQUE NOT NULL,
                attack_type TEXT NOT NULL,
                trigger_condition TEXT NOT NULL,
                action_type TEXT NOT NULL,
                threshold INTEGER NOT NULL,
                time_window_minutes INTEGER DEFAULT 60,
                enabled BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        print("  - auto_response_rules table created")
        
        cursor.execute('''
            INSERT INTO auto_response_rules 
            (rule_name, attack_type, trigger_condition, action_type, threshold, time_window_minutes, enabled)
            VALUES 
            ('Auto-block brute force', 'login_brute_force', 'failed_attempts', 'block_ip', 5, 10, 1),
            ('Auto-block SQL injection', 'sql_injection', 'attack_count', 'block_ip', 3, 60, 1),
            ('Auto-lock compromised account', 'login_brute_force', 'failed_login_per_user', 'lock_account', 5, 15, 1),
            ('Rate limit violators', 'rate_limit_violation', 'requests_per_minute', 'block_ip', 100, 1, 1),
            ('Block privilege escalation', 'privilege_escalation', 'attack_count', 'block_ip', 1, 60, 1)
        ''')
        print("  - Default auto-response rules inserted")
    except sqlite3.OperationalError:
        print("  - auto_response_rules table already exists")
    
    try:
        cursor.execute('''
            CREATE TABLE users_locked (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE NOT NULL,
                locked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                locked_until TIMESTAMP,
                reason TEXT NOT NULL,
                locked_by INTEGER,
                security_action_id INTEGER,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (locked_by) REFERENCES users(id),
                FOREIGN KEY (security_action_id) REFERENCES security_actions(id)
            )
        ''')
        print("  - users_locked table created")
    except sqlite3.OperationalError:
        print("  - users_locked table already exists")
    
    print("Creating indexes...")
    
    try:
        cursor.execute('CREATE INDEX idx_attack_logs_ip ON attack_logs(ip_address)')
        print("  - idx_attack_logs_ip created")
    except sqlite3.OperationalError:
        print("  - idx_attack_logs_ip already exists")
    
    try:
        cursor.execute('CREATE INDEX idx_attack_logs_timestamp ON attack_logs(timestamp)')
        print("  - idx_attack_logs_timestamp created")
    except sqlite3.OperationalError:
        print("  - idx_attack_logs_timestamp already exists")
    
    try:
        cursor.execute('CREATE INDEX idx_attack_logs_type ON attack_logs(attack_type)')
        print("  - idx_attack_logs_type created")
    except sqlite3.OperationalError:
        print("  - idx_attack_logs_type already exists")
    
    try:
        cursor.execute('CREATE INDEX idx_attack_logs_risk ON attack_logs(risk_score)')
        print("  - idx_attack_logs_risk created")
    except sqlite3.OperationalError:
        print("  - idx_attack_logs_risk already exists")
    
    try:
        cursor.execute('CREATE INDEX idx_blocked_ips_active ON blocked_ips(ip_address, is_active)')
        print("  - idx_blocked_ips_active created")
    except sqlite3.OperationalError:
        print("  - idx_blocked_ips_active already exists")
    
    try:
        cursor.execute('CREATE INDEX idx_failed_logins_username ON failed_login_attempts(username)')
        print("  - idx_failed_logins_username created")
    except sqlite3.OperationalError:
        print("  - idx_failed_logins_username already exists")
    
    try:
        cursor.execute('CREATE INDEX idx_failed_logins_ip ON failed_login_attempts(ip_address)')
        print("  - idx_failed_logins_ip created")
    except sqlite3.OperationalError:
        print("  - idx_failed_logins_ip already exists")
    
    try:
        cursor.execute('CREATE INDEX idx_failed_logins_time ON failed_login_attempts(attempt_time)')
        print("  - idx_failed_logins_time created")
    except sqlite3.OperationalError:
        print("  - idx_failed_logins_time already exists")
    
    conn.commit()
    conn.close()
    
    print("\nMigration completed successfully!")
    print(f"Backup saved at: {backup_path}")
    print("\nNew features available:")
    print("  - Enhanced attack logging with risk scores and classifications")
    print("  - IP blocking and unblocking")
    print("  - Account locking/unlocking")
    print("  - Failed login attempt tracking")
    print("  - Security action audit trail")
    print("  - Automated response rules")
    print("  - Attack chain tracking")

if __name__ == '__main__':
    migrate_database()
