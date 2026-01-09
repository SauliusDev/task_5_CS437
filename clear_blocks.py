import sqlite3

conn = sqlite3.connect('/app/database/valves.db')
cursor = conn.cursor()

cursor.execute("DELETE FROM blocked_ip")
cursor.execute("DELETE FROM user_locked")
conn.commit()

print("Cleared blocked IPs and locked users")
conn.close()
