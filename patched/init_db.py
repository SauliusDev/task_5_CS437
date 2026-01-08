import sqlite3
import os

DATABASE_PATH = 'database/valves.db'

def init_database():
    os.makedirs('database', exist_ok=True)
    
    if os.path.exists(DATABASE_PATH):
        print(f"Database already exists at {DATABASE_PATH}")
        return
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('admin', 'operator')),
            email TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE valves (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            valve_name TEXT UNIQUE NOT NULL,
            location TEXT NOT NULL,
            open_percentage INTEGER DEFAULT 0 CHECK(open_percentage BETWEEN 0 AND 100),
            status TEXT DEFAULT 'operational' CHECK(status IN ('operational', 'maintenance', 'error', 'offline')),
            communication_status TEXT DEFAULT 'connected' CHECK(communication_status IN ('connected', 'disconnected', 'timeout')),
            last_command TEXT,
            last_command_timestamp TIMESTAMP,
            last_response_timestamp TIMESTAMP,
            firmware_version TEXT DEFAULT '1.0.0',
            config_file TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE command_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            valve_id INTEGER NOT NULL,
            command TEXT NOT NULL,
            user_id INTEGER NOT NULL,
            target_percentage INTEGER,
            status TEXT CHECK(status IN ('success', 'failed', 'timeout')),
            response_time_ms INTEGER,
            error_message TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (valve_id) REFERENCES valves(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE schedules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            valve_id INTEGER NOT NULL,
            scheduled_time TIMESTAMP NOT NULL,
            command TEXT NOT NULL,
            target_percentage INTEGER,
            created_by INTEGER NOT NULL,
            status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'executed', 'cancelled', 'failed')),
            executed_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (valve_id) REFERENCES valves(id),
            FOREIGN KEY (created_by) REFERENCES users(id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE file_uploads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_filename TEXT NOT NULL,
            stored_filename TEXT NOT NULL,
            file_type TEXT CHECK(file_type IN ('firmware', 'config', 'encrypted')),
            file_size INTEGER NOT NULL,
            upload_endpoint TEXT NOT NULL,
            uploaded_by INTEGER NOT NULL,
            is_encrypted BOOLEAN DEFAULT 0,
            scan_status TEXT CHECK(scan_status IN ('pending', 'clean', 'malicious', 'skipped')),
            applied_to_valve INTEGER,
            upload_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (uploaded_by) REFERENCES users(id),
            FOREIGN KEY (applied_to_valve) REFERENCES valves(id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE attack_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            attack_type TEXT NOT NULL CHECK(attack_type IN (
                'sql_injection', 
                'file_upload_abuse', 
                'size_bypass', 
                'mime_bypass',
                'encrypted_payload',
                'suspicious_activity',
                'login_brute_force',
                'directory_brute_force',
                'session_hijacking',
                'cookie_manipulation',
                'rate_limit_violation',
                'privilege_escalation',
                'path_traversal',
                'csrf_attempt',
                'xss_attempt',
                'unauthorized_access'
            )),
            endpoint TEXT NOT NULL,
            user_id INTEGER,
            ip_address TEXT,
            user_agent TEXT,
            request_method TEXT,
            payload TEXT,
            severity TEXT CHECK(severity IN ('low', 'medium', 'high', 'critical')),
            blocked BOOLEAN DEFAULT 0,
            details TEXT,
            classification TEXT,
            recommended_action TEXT,
            action_taken TEXT,
            action_reversible BOOLEAN DEFAULT 1,
            reverse_action_steps TEXT,
            risk_score INTEGER DEFAULT 0 CHECK(risk_score BETWEEN 0 AND 100),
            related_attack_id INTEGER,
            raw_request_data TEXT,
            response_status INTEGER,
            geolocation TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (related_attack_id) REFERENCES attack_logs(id)
        )
    ''')
    
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
    
    cursor.execute('CREATE INDEX idx_attack_logs_ip ON attack_logs(ip_address)')
    cursor.execute('CREATE INDEX idx_attack_logs_timestamp ON attack_logs(timestamp)')
    cursor.execute('CREATE INDEX idx_attack_logs_type ON attack_logs(attack_type)')
    cursor.execute('CREATE INDEX idx_attack_logs_risk ON attack_logs(risk_score)')
    cursor.execute('CREATE INDEX idx_blocked_ips_active ON blocked_ips(ip_address, is_active)')
    cursor.execute('CREATE INDEX idx_failed_logins_username ON failed_login_attempts(username)')
    cursor.execute('CREATE INDEX idx_failed_logins_ip ON failed_login_attempts(ip_address)')
    cursor.execute('CREATE INDEX idx_failed_logins_time ON failed_login_attempts(attempt_time)')
    
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
    
    conn.commit()
    conn.close()
    
    print(f"Database initialized successfully at {DATABASE_PATH}")

if __name__ == '__main__':
    init_database()

