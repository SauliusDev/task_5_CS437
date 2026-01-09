import sqlite3

conn = sqlite3.connect('/app/instance/scada.db')
cursor = conn.cursor()

cursor.execute("DELETE FROM blocked_ip")
cursor.execute("DELETE FROM user_locked")
conn.commit()

print(f"Cleared {cursor.rowcount} blocked IPs and locked users")
conn.close()
