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
                'suspicious_activity'
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
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    conn.commit()
    conn.close()
    
    print(f"Database initialized successfully at {DATABASE_PATH}")

if __name__ == '__main__':
    init_database()

