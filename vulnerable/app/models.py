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

class BlockedIP:
    @staticmethod
    def create(ip_address, reason, blocked_until=None, auto_unblock=False, blocked_by_user_id=None, attack_log_id=None):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            '''INSERT INTO blocked_ips 
               (ip_address, reason, blocked_until, auto_unblock, blocked_by_user_id, attack_log_id)
               VALUES (?, ?, ?, ?, ?, ?)''',
            (ip_address, reason, blocked_until, auto_unblock, blocked_by_user_id, attack_log_id)
        )
        conn.commit()
        blocked_id = cursor.lastrowid
        conn.close()
        return blocked_id
    
    @staticmethod
    def is_blocked(ip_address):
        conn = get_db_connection()
        blocked = conn.execute(
            '''SELECT * FROM blocked_ips 
               WHERE ip_address = ? AND is_active = 1
               AND (blocked_until IS NULL OR blocked_until > datetime("now"))''',
            (ip_address,)
        ).fetchone()
        conn.close()
        return dict(blocked) if blocked else None
    
    @staticmethod
    def unblock(ip_address):
        conn = get_db_connection()
        conn.execute(
            'UPDATE blocked_ips SET is_active = 0 WHERE ip_address = ?',
            (ip_address,)
        )
        conn.commit()
        conn.close()
    
    @staticmethod
    def get_all_active():
        conn = get_db_connection()
        blocked = conn.execute(
            '''SELECT bi.*, u.username as blocked_by_username
               FROM blocked_ips bi
               LEFT JOIN users u ON bi.blocked_by_user_id = u.id
               WHERE bi.is_active = 1
               ORDER BY bi.blocked_at DESC'''
        ).fetchall()
        conn.close()
        return [dict(b) for b in blocked]
    
    @staticmethod
    def cleanup_expired():
        conn = get_db_connection()
        conn.execute(
            '''UPDATE blocked_ips SET is_active = 0 
               WHERE blocked_until IS NOT NULL 
               AND blocked_until < datetime("now")
               AND auto_unblock = 1'''
        )
        conn.commit()
        conn.close()

class FailedLoginTracker:
    @staticmethod
    def create(username, ip_address, user_agent=None, attack_log_id=None):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            '''INSERT INTO failed_login_attempts 
               (username, ip_address, user_agent, attack_log_id)
               VALUES (?, ?, ?, ?)''',
            (username, ip_address, user_agent, attack_log_id)
        )
        conn.commit()
        attempt_id = cursor.lastrowid
        conn.close()
        return attempt_id
    
    @staticmethod
    def get_recent_by_username(username, minutes=15):
        conn = get_db_connection()
        attempts = conn.execute(
            '''SELECT * FROM failed_login_attempts 
               WHERE username = ? 
               AND attempt_time > datetime("now", "-" || ? || " minutes")
               ORDER BY attempt_time DESC''',
            (username, minutes)
        ).fetchall()
        conn.close()
        return [dict(a) for a in attempts]
    
    @staticmethod
    def get_recent_by_ip(ip_address, minutes=15):
        conn = get_db_connection()
        attempts = conn.execute(
            '''SELECT * FROM failed_login_attempts 
               WHERE ip_address = ? 
               AND attempt_time > datetime("now", "-" || ? || " minutes")
               ORDER BY attempt_time DESC''',
            (ip_address, minutes)
        ).fetchall()
        conn.close()
        return [dict(a) for a in attempts]
    
    @staticmethod
    def cleanup_old(days=7):
        conn = get_db_connection()
        conn.execute(
            'DELETE FROM failed_login_attempts WHERE attempt_time < datetime("now", "-" || ? || " days")',
            (days,)
        )
        conn.commit()
        conn.close()

class SecurityAction:
    @staticmethod
    def create(action_type, target, reason, executed_by=None, attack_log_id=None, automated=False):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            '''INSERT INTO security_actions 
               (action_type, target, reason, executed_by, attack_log_id, automated)
               VALUES (?, ?, ?, ?, ?, ?)''',
            (action_type, target, reason, executed_by, attack_log_id, automated)
        )
        conn.commit()
        action_id = cursor.lastrowid
        conn.close()
        return action_id
    
    @staticmethod
    def reverse_action(action_id, reversed_by):
        conn = get_db_connection()
        conn.execute(
            'UPDATE security_actions SET reversed_at = datetime("now"), reversed_by = ? WHERE id = ?',
            (reversed_by, action_id)
        )
        conn.commit()
        conn.close()
    
    @staticmethod
    def get_all(limit=100):
        conn = get_db_connection()
        actions = conn.execute(
            '''SELECT sa.*, 
                      u1.username as executed_by_username,
                      u2.username as reversed_by_username
               FROM security_actions sa
               LEFT JOIN users u1 ON sa.executed_by = u1.id
               LEFT JOIN users u2 ON sa.reversed_by = u2.id
               ORDER BY sa.executed_at DESC LIMIT ?''',
            (limit,)
        ).fetchall()
        conn.close()
        return [dict(a) for a in actions]
    
    @staticmethod
    def get_active():
        conn = get_db_connection()
        actions = conn.execute(
            '''SELECT sa.*, 
                      u1.username as executed_by_username
               FROM security_actions sa
               LEFT JOIN users u1 ON sa.executed_by = u1.id
               WHERE sa.reversed_at IS NULL
               ORDER BY sa.executed_at DESC'''
        ).fetchall()
        conn.close()
        return [dict(a) for a in actions]

class AutoResponseRule:
    @staticmethod
    def get_all():
        conn = get_db_connection()
        rules = conn.execute(
            'SELECT * FROM auto_response_rules ORDER BY rule_name'
        ).fetchall()
        conn.close()
        return [dict(r) for r in rules]
    
    @staticmethod
    def get_enabled():
        conn = get_db_connection()
        rules = conn.execute(
            'SELECT * FROM auto_response_rules WHERE enabled = 1'
        ).fetchall()
        conn.close()
        return [dict(r) for r in rules]
    
    @staticmethod
    def get_by_attack_type(attack_type):
        conn = get_db_connection()
        rules = conn.execute(
            'SELECT * FROM auto_response_rules WHERE attack_type = ? AND enabled = 1',
            (attack_type,)
        ).fetchall()
        conn.close()
        return [dict(r) for r in rules]
    
    @staticmethod
    def toggle_enabled(rule_id):
        conn = get_db_connection()
        conn.execute(
            'UPDATE auto_response_rules SET enabled = NOT enabled, updated_at = datetime("now") WHERE id = ?',
            (rule_id,)
        )
        conn.commit()
        conn.close()
    
    @staticmethod
    def update_threshold(rule_id, threshold):
        conn = get_db_connection()
        conn.execute(
            'UPDATE auto_response_rules SET threshold = ?, updated_at = datetime("now") WHERE id = ?',
            (threshold, rule_id)
        )
        conn.commit()
        conn.close()

class UserLocked:
    @staticmethod
    def lock_user(user_id, reason, locked_until=None, locked_by=None, security_action_id=None):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            '''INSERT OR REPLACE INTO users_locked 
               (user_id, locked_until, reason, locked_by, security_action_id)
               VALUES (?, ?, ?, ?, ?)''',
            (user_id, locked_until, reason, locked_by, security_action_id)
        )
        conn.commit()
        lock_id = cursor.lastrowid
        conn.close()
        return lock_id
    
    @staticmethod
    def is_locked(user_id):
        conn = get_db_connection()
        locked = conn.execute(
            '''SELECT * FROM users_locked 
               WHERE user_id = ?
               AND (locked_until IS NULL OR locked_until > datetime("now"))''',
            (user_id,)
        ).fetchone()
        conn.close()
        return dict(locked) if locked else None
    
    @staticmethod
    def unlock_user(user_id):
        conn = get_db_connection()
        conn.execute(
            'DELETE FROM users_locked WHERE user_id = ?',
            (user_id,)
        )
        conn.commit()
        conn.close()
    
    @staticmethod
    def get_all_locked():
        conn = get_db_connection()
        locked = conn.execute(
            '''SELECT ul.*, u.username, u2.username as locked_by_username
               FROM users_locked ul
               JOIN users u ON ul.user_id = u.id
               LEFT JOIN users u2 ON ul.locked_by = u2.id
               ORDER BY ul.locked_at DESC'''
        ).fetchall()
        conn.close()
        return [dict(l) for l in locked]

class AttackLog:
    @staticmethod
    def create(attack_type, endpoint, user_id, ip_address, user_agent, request_method, payload, severity, 
               blocked=False, details=None, classification=None, recommended_action=None, action_taken=None,
               action_reversible=True, reverse_action_steps=None, risk_score=0, related_attack_id=None,
               raw_request_data=None, response_status=None, geolocation=None):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            '''INSERT INTO attack_logs 
               (attack_type, endpoint, user_id, ip_address, user_agent, request_method, payload, severity, 
                blocked, details, classification, recommended_action, action_taken, action_reversible, 
                reverse_action_steps, risk_score, related_attack_id, raw_request_data, response_status, geolocation)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (attack_type, endpoint, user_id, ip_address, user_agent, request_method, payload, severity, 
             blocked, details, classification, recommended_action, action_taken, action_reversible,
             reverse_action_steps, risk_score, related_attack_id, raw_request_data, response_status, geolocation)
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
    def get_by_ip(ip_address, limit=100):
        conn = get_db_connection()
        logs = conn.execute(
            '''SELECT al.*, u.username 
               FROM attack_logs al
               LEFT JOIN users u ON al.user_id = u.id
               WHERE al.ip_address = ?
               ORDER BY al.timestamp DESC LIMIT ?''',
            (ip_address, limit)
        ).fetchall()
        conn.close()
        return [dict(log) for log in logs]
    
    @staticmethod
    def get_recent_by_ip(ip_address, minutes=60):
        conn = get_db_connection()
        logs = conn.execute(
            '''SELECT * FROM attack_logs 
               WHERE ip_address = ? 
               AND timestamp > datetime("now", "-" || ? || " minutes")
               ORDER BY timestamp DESC''',
            (ip_address, minutes)
        ).fetchall()
        conn.close()
        return [dict(log) for log in logs]
    
    @staticmethod
    def get_high_risk(threshold=70, limit=100):
        conn = get_db_connection()
        logs = conn.execute(
            '''SELECT al.*, u.username 
               FROM attack_logs al
               LEFT JOIN users u ON al.user_id = u.id
               WHERE al.risk_score >= ?
               ORDER BY al.risk_score DESC, al.timestamp DESC LIMIT ?''',
            (threshold, limit)
        ).fetchall()
        conn.close()
        return [dict(log) for log in logs]
    
    @staticmethod
    def get_actionable(limit=100):
        conn = get_db_connection()
        logs = conn.execute(
            '''SELECT al.*, u.username 
               FROM attack_logs al
               LEFT JOIN users u ON al.user_id = u.id
               WHERE al.recommended_action IS NOT NULL 
               AND al.recommended_action != 'log_only'
               AND (al.action_taken IS NULL OR al.action_taken = '')
               ORDER BY al.risk_score DESC, al.timestamp DESC LIMIT ?''',
            (limit,)
        ).fetchall()
        conn.close()
        return [dict(log) for log in logs]
    
    @staticmethod
    def get_attack_chains(attack_id):
        conn = get_db_connection()
        logs = conn.execute(
            '''SELECT al.*, u.username 
               FROM attack_logs al
               LEFT JOIN users u ON al.user_id = u.id
               WHERE al.related_attack_id = ? OR al.id = ?
               ORDER BY al.timestamp''',
            (attack_id, attack_id)
        ).fetchall()
        conn.close()
        return [dict(log) for log in logs]
    
    @staticmethod
    def mark_action_taken(attack_id, action_taken):
        conn = get_db_connection()
        conn.execute(
            'UPDATE attack_logs SET action_taken = ? WHERE id = ?',
            (action_taken, attack_id)
        )
        conn.commit()
        conn.close()
    
    @staticmethod
    def get_by_type(attack_type, limit=100):
        conn = get_db_connection()
        logs = conn.execute(
            '''SELECT al.*, u.username 
               FROM attack_logs al
               LEFT JOIN users u ON al.user_id = u.id
               WHERE al.attack_type = ?
               ORDER BY al.timestamp DESC LIMIT ?''',
            (attack_type, limit)
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
        
        high_risk = conn.execute(
            'SELECT COUNT(*) as count FROM attack_logs WHERE risk_score >= 70'
        ).fetchone()['count']
        
        actionable = conn.execute(
            '''SELECT COUNT(*) as count FROM attack_logs 
               WHERE recommended_action IS NOT NULL 
               AND recommended_action != 'log_only'
               AND (action_taken IS NULL OR action_taken = '')'''
        ).fetchone()['count']
        
        conn.close()
        
        return {
            'total': total,
            'by_type': {row['attack_type']: row['count'] for row in by_type},
            'by_severity': {row['severity']: row['count'] for row in by_severity},
            'recent_24h': recent,
            'high_risk': high_risk,
            'actionable': actionable
        }

