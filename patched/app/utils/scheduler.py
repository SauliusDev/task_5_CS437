from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import sqlite3
import random

DATABASE_PATH = 'database/valves.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def execute_scheduled_commands():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    schedules = cursor.execute('''
        SELECT s.*, v.valve_name 
        FROM schedules s
        JOIN valves v ON s.valve_id = v.id
        WHERE s.status = 'pending' 
        AND datetime(s.scheduled_time) <= datetime('now')
    ''').fetchall()
    
    for schedule in schedules:
        try:
            command = schedule['command']
            valve_id = schedule['valve_id']
            target_percentage = schedule['target_percentage']
            
            if command == 'OPEN':
                target_percentage = 100
            elif command == 'CLOSE':
                target_percentage = 0
            elif command == 'SYNC':
                valve = cursor.execute('SELECT open_percentage FROM valves WHERE id = ?', (valve_id,)).fetchone()
                target_percentage = valve['open_percentage']
            
            success = random.random() > 0.1
            response_time = random.randint(50, 500) if success else random.randint(1000, 5000)
            
            if success:
                cursor.execute('''
                    UPDATE valves 
                    SET open_percentage = ?,
                        last_command = ?,
                        last_command_timestamp = datetime('now'),
                        last_response_timestamp = datetime('now'),
                        updated_at = datetime('now')
                    WHERE id = ?
                ''', (target_percentage, command, valve_id))
                
                cursor.execute('''
                    INSERT INTO command_logs 
                    (valve_id, command, user_id, target_percentage, status, response_time_ms)
                    VALUES (?, ?, ?, ?, 'success', ?)
                ''', (valve_id, command, schedule['created_by'], target_percentage, response_time))
                
                cursor.execute('''
                    UPDATE schedules 
                    SET status = 'executed', executed_at = datetime('now')
                    WHERE id = ?
                ''', (schedule['id'],))
            else:
                error_msg = random.choice(['Connection timeout', 'Hardware error', 'Invalid response'])
                
                cursor.execute('''
                    INSERT INTO command_logs 
                    (valve_id, command, user_id, target_percentage, status, response_time_ms, error_message)
                    VALUES (?, ?, ?, ?, 'failed', ?, ?)
                ''', (valve_id, command, schedule['created_by'], target_percentage, response_time, error_msg))
                
                cursor.execute('''
                    UPDATE schedules 
                    SET status = 'failed', executed_at = datetime('now')
                    WHERE id = ?
                ''', (schedule['id'],))
            
            conn.commit()
            
        except Exception as e:
            cursor.execute('''
                UPDATE schedules 
                SET status = 'failed', executed_at = datetime('now')
                WHERE id = ?
            ''', (schedule['id'],))
            conn.commit()
    
    conn.close()

scheduler = None

def start_scheduler():
    global scheduler
    if scheduler is None:
        scheduler = BackgroundScheduler()
        scheduler.add_job(func=execute_scheduled_commands, trigger="interval", seconds=30)
        scheduler.start()

def stop_scheduler():
    global scheduler
    if scheduler is not None:
        scheduler.shutdown()
        scheduler = None
