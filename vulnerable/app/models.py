import sqlite3
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

DATABASE_PATH = 'database/valves.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

class User:
    @staticmethod
    def create(username, password, role, email=None):
        conn = get_db_connection()
        password_hash = generate_password_hash(password)
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO users (username, password_hash, role, email) VALUES (?, ?, ?, ?)',
            (username, password_hash, role, email)
        )
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        return user_id

    @staticmethod
    def authenticate(username, password):
        conn = get_db_connection()
        user = conn.execute(
            'SELECT * FROM users WHERE username = ?',
            (username,)
        ).fetchone()
        conn.close()
        
        if user and check_password_hash(user['password_hash'], password):
            return dict(user)
        return None

    @staticmethod
    def get_by_id(user_id):
        conn = get_db_connection()
        user = conn.execute(
            'SELECT id, username, role, email, created_at, last_login FROM users WHERE id = ?',
            (user_id,)
        ).fetchone()
        conn.close()
        return dict(user) if user else None

    @staticmethod
    def update_last_login(user_id):
        conn = get_db_connection()
        conn.execute(
            'UPDATE users SET last_login = ? WHERE id = ?',
            (datetime.now(), user_id)
        )
        conn.commit()
        conn.close()

class Valve:
    @staticmethod
    def get_all():
        conn = get_db_connection()
        valves = conn.execute('SELECT * FROM valves ORDER BY valve_name').fetchall()
        conn.close()
        return [dict(valve) for valve in valves]

    @staticmethod
    def get_by_id(valve_id):
        conn = get_db_connection()
        valve = conn.execute('SELECT * FROM valves WHERE id = ?', (valve_id,)).fetchone()
        conn.close()
        return dict(valve) if valve else None

    @staticmethod
    def search(search_term):
        conn = get_db_connection()
        valves = conn.execute(
            'SELECT * FROM valves WHERE valve_name LIKE ? OR location LIKE ? ORDER BY valve_name',
            (f'%{search_term}%', f'%{search_term}%')
        ).fetchall()
        conn.close()
        return [dict(valve) for valve in valves]

    @staticmethod
    def update_status(valve_id, open_percentage, command, user_id):
        conn = get_db_connection()
        now = datetime.now()
        
        conn.execute(
            '''UPDATE valves SET 
               open_percentage = ?, 
               last_command = ?, 
               last_command_timestamp = ?,
               last_response_timestamp = ?,
               updated_at = ?
               WHERE id = ?''',
            (open_percentage, command, now, now, now, valve_id)
        )
        conn.commit()
        conn.close()

    @staticmethod
    def update_communication_status(valve_id, status):
        conn = get_db_connection()
        conn.execute(
            'UPDATE valves SET communication_status = ?, updated_at = ? WHERE id = ?',
            (status, datetime.now(), valve_id)
        )
        conn.commit()
        conn.close()

class CommandLog:
    @staticmethod
    def create(valve_id, command, user_id, target_percentage, status, response_time_ms=None, error_message=None):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            '''INSERT INTO command_logs 
               (valve_id, command, user_id, target_percentage, status, response_time_ms, error_message)
               VALUES (?, ?, ?, ?, ?, ?, ?)''',
            (valve_id, command, user_id, target_percentage, status, response_time_ms, error_message)
        )
        conn.commit()
        log_id = cursor.lastrowid
        conn.close()
        return log_id

    @staticmethod
    def get_by_valve(valve_id, limit=50):
        conn = get_db_connection()
        logs = conn.execute(
            '''SELECT cl.*, u.username, v.valve_name 
               FROM command_logs cl
               JOIN users u ON cl.user_id = u.id
               JOIN valves v ON cl.valve_id = v.id
               WHERE cl.valve_id = ?
               ORDER BY cl.timestamp DESC LIMIT ?''',
            (valve_id, limit)
        ).fetchall()
        conn.close()
        return [dict(log) for log in logs]

    @staticmethod
    def get_all(limit=100):
        conn = get_db_connection()
        logs = conn.execute(
            '''SELECT cl.*, u.username, v.valve_name 
               FROM command_logs cl
               JOIN users u ON cl.user_id = u.id
               JOIN valves v ON cl.valve_id = v.id
               ORDER BY cl.timestamp DESC LIMIT ?''',
            (limit,)
        ).fetchall()
        conn.close()
        return [dict(log) for log in logs]

    @staticmethod
    def get_failed(limit=100):
        conn = get_db_connection()
        logs = conn.execute(
            '''SELECT cl.*, u.username, v.valve_name 
               FROM command_logs cl
               JOIN users u ON cl.user_id = u.id
               JOIN valves v ON cl.valve_id = v.id
               WHERE cl.status = 'failed'
               ORDER BY cl.timestamp DESC LIMIT ?''',
            (limit,)
        ).fetchall()
        conn.close()
        return [dict(log) for log in logs]

    @staticmethod
    def get_timeouts(limit=100):
        conn = get_db_connection()
        logs = conn.execute(
            '''SELECT cl.*, u.username, v.valve_name 
               FROM command_logs cl
               JOIN users u ON cl.user_id = u.id
               JOIN valves v ON cl.valve_id = v.id
               WHERE cl.status = 'timeout'
               ORDER BY cl.timestamp DESC LIMIT ?''',
            (limit,)
        ).fetchall()
        conn.close()
        return [dict(log) for log in logs]

class Schedule:
    @staticmethod
    def create(valve_id, scheduled_time, command, target_percentage, created_by):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            '''INSERT INTO schedules 
               (valve_id, scheduled_time, command, target_percentage, created_by)
               VALUES (?, ?, ?, ?, ?)''',
            (valve_id, scheduled_time, command, target_percentage, created_by)
        )
        conn.commit()
        schedule_id = cursor.lastrowid
        conn.close()
        return schedule_id

    @staticmethod
    def get_all():
        conn = get_db_connection()
        schedules = conn.execute(
            '''SELECT s.*, v.valve_name, u.username 
               FROM schedules s
               JOIN valves v ON s.valve_id = v.id
               JOIN users u ON s.created_by = u.id
               ORDER BY s.scheduled_time''',
        ).fetchall()
        conn.close()
        return [dict(schedule) for schedule in schedules]

    @staticmethod
    def get_pending():
        conn = get_db_connection()
        schedules = conn.execute(
            '''SELECT s.*, v.valve_name, u.username 
               FROM schedules s
               JOIN valves v ON s.valve_id = v.id
               JOIN users u ON s.created_by = u.id
               WHERE s.status = 'pending'
               ORDER BY s.scheduled_time''',
        ).fetchall()
        conn.close()
        return [dict(schedule) for schedule in schedules]

    @staticmethod
    def cancel(schedule_id):
        conn = get_db_connection()
        conn.execute(
            'UPDATE schedules SET status = ? WHERE id = ?',
            ('cancelled', schedule_id)
        )
        conn.commit()
        conn.close()

class FileUpload:
    @staticmethod
    def create(original_filename, stored_filename, file_type, file_size, upload_endpoint, uploaded_by, is_encrypted=False, applied_to_valve=None):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            '''INSERT INTO file_uploads 
               (original_filename, stored_filename, file_type, file_size, upload_endpoint, uploaded_by, is_encrypted, scan_status, applied_to_valve)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (original_filename, stored_filename, file_type, file_size, upload_endpoint, uploaded_by, is_encrypted, 'clean', applied_to_valve)
        )
        conn.commit()
        upload_id = cursor.lastrowid
        conn.close()
        return upload_id

    @staticmethod
    def get_all():
        conn = get_db_connection()
        uploads = conn.execute(
            '''SELECT fu.*, u.username 
               FROM file_uploads fu
               JOIN users u ON fu.uploaded_by = u.id
               ORDER BY fu.upload_timestamp DESC''',
        ).fetchall()
        conn.close()
        return [dict(upload) for upload in uploads]

class AttackLog:
    @staticmethod
    def create(attack_type, endpoint, user_id, ip_address, user_agent, request_method, payload, severity, blocked=False, details=None):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            '''INSERT INTO attack_logs 
               (attack_type, endpoint, user_id, ip_address, user_agent, request_method, payload, severity, blocked, details)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (attack_type, endpoint, user_id, ip_address, user_agent, request_method, payload, severity, blocked, details)
        )
        conn.commit()
        log_id = cursor.lastrowid
        conn.close()
        return log_id

    @staticmethod
    def get_all(limit=100):
        conn = get_db_connection()
        logs = conn.execute(
            '''SELECT al.*, u.username 
               FROM attack_logs al
               LEFT JOIN users u ON al.user_id = u.id
               ORDER BY al.timestamp DESC LIMIT ?''',
            (limit,)
        ).fetchall()
        conn.close()
        return [dict(log) for log in logs]

    @staticmethod
    def get_statistics():
        conn = get_db_connection()
        
        total = conn.execute('SELECT COUNT(*) as count FROM attack_logs').fetchone()['count']
        
        by_type = conn.execute(
            'SELECT attack_type, COUNT(*) as count FROM attack_logs GROUP BY attack_type'
        ).fetchall()
        
        by_severity = conn.execute(
            'SELECT severity, COUNT(*) as count FROM attack_logs GROUP BY severity'
        ).fetchall()
        
        recent = conn.execute(
            'SELECT COUNT(*) as count FROM attack_logs WHERE timestamp > datetime("now", "-24 hours")'
        ).fetchone()['count']
        
        conn.close()
        
        return {
            'total': total,
            'by_type': {row['attack_type']: row['count'] for row in by_type},
            'by_severity': {row['severity']: row['count'] for row in by_severity},
            'recent_24h': recent
        }

