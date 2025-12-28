import sqlite3
import random
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash

DATABASE_PATH = 'database/valves.db'

def populate_database():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    print("Populating database with initial data...")
    
    cursor.execute('DELETE FROM users')
    cursor.execute('DELETE FROM valves')
    print("Cleared existing data")
    
    admin_hash = generate_password_hash('admin123')
    operator_hash = generate_password_hash('operator123')
    
    cursor.execute(
        'INSERT INTO users (username, password_hash, role, email) VALUES (?, ?, ?, ?)',
        ('admin', admin_hash, 'admin', 'admin@valvecontrol.local')
    )
    cursor.execute(
        'INSERT INTO users (username, password_hash, role, email) VALUES (?, ?, ?, ?)',
        ('operator', operator_hash, 'operator', 'operator@valvecontrol.local')
    )
    print("Created default users: admin/admin123, operator/operator123")
    
    buildings = ['Building-A', 'Building-B', 'Building-C', 'Building-D', 'Building-E']
    sectors = ['Sector-1', 'Sector-2', 'Sector-3', 'Sector-4', 'Sector-5', 
               'Sector-6', 'Sector-7', 'Sector-8', 'Sector-9', 'Sector-10']
    
    statuses = ['operational', 'operational', 'operational', 'operational', 'maintenance', 'error', 'offline']
    comm_statuses = ['connected', 'connected', 'connected', 'connected', 'disconnected', 'timeout']
    
    firmware_versions = ['1.0.0', '1.0.1', '1.1.0', '1.2.0', '2.0.0']
    
    valve_count = 150
    
    for i in range(1, valve_count + 1):
        valve_name = f'V-{i:03d}'
        location = f"{random.choice(buildings)}, {random.choice(sectors)}"
        open_percentage = random.randint(0, 100)
        status = random.choice(statuses)
        comm_status = random.choice(comm_statuses)
        firmware_version = random.choice(firmware_versions)
        
        last_command = random.choice(['OPEN', 'CLOSE', 'ADJUST', 'SYNC', None])
        
        if last_command:
            last_command_time = datetime.now() - timedelta(
                hours=random.randint(0, 72),
                minutes=random.randint(0, 59)
            )
            last_response_time = last_command_time + timedelta(milliseconds=random.randint(50, 500))
        else:
            last_command_time = None
            last_response_time = None
        
        cursor.execute('''
            INSERT INTO valves 
            (valve_name, location, open_percentage, status, communication_status, 
             last_command, last_command_timestamp, last_response_timestamp, firmware_version)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (valve_name, location, open_percentage, status, comm_status, 
              last_command, last_command_time, last_response_time, firmware_version))
    
    print(f"Created {valve_count} valve records")
    
    cursor.execute('SELECT id FROM users WHERE username = ?', ('admin',))
    admin_id = cursor.fetchone()[0]
    cursor.execute('SELECT id FROM users WHERE username = ?', ('operator',))
    operator_id = cursor.fetchone()[0]
    
    cursor.execute('SELECT id FROM valves LIMIT 20')
    valve_ids = [row[0] for row in cursor.fetchall()]
    
    log_count = 50
    for _ in range(log_count):
        valve_id = random.choice(valve_ids)
        command = random.choice(['OPEN', 'CLOSE', 'ADJUST', 'SYNC'])
        user_id = random.choice([admin_id, operator_id])
        target_percentage = random.randint(0, 100) if command == 'ADJUST' else None
        status = random.choice(['success', 'success', 'success', 'failed', 'timeout'])
        response_time = random.randint(50, 500) if status == 'success' else random.randint(1000, 5000)
        error_message = random.choice([None, 'Connection timeout', 'Hardware error', 'Invalid response']) if status != 'success' else None
        
        cursor.execute('''
            INSERT INTO command_logs 
            (valve_id, command, user_id, target_percentage, status, response_time_ms, error_message)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (valve_id, command, user_id, target_percentage, status, response_time, error_message))
    
    print(f"Created {log_count} command log entries")
    
    schedule_count = 10
    for _ in range(schedule_count):
        valve_id = random.choice(valve_ids)
        scheduled_time = datetime.now() + timedelta(hours=random.randint(1, 48))
        command = random.choice(['OPEN', 'CLOSE', 'ADJUST'])
        target_percentage = random.randint(0, 100) if command == 'ADJUST' else None
        created_by = random.choice([admin_id, operator_id])
        
        cursor.execute('''
            INSERT INTO schedules 
            (valve_id, scheduled_time, command, target_percentage, created_by)
            VALUES (?, ?, ?, ?, ?)
        ''', (valve_id, scheduled_time, command, target_percentage, created_by))
    
    print(f"Created {schedule_count} scheduled operations")
    
    conn.commit()
    conn.close()
    
    print("\nDatabase population complete!")
    print(f"Total valves: {valve_count}")
    print(f"Total command logs: {log_count}")
    print(f"Total schedules: {schedule_count}")

if __name__ == '__main__':
    populate_database()

