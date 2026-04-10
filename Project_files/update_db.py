import sqlite3
conn = sqlite3.connect('school_system.db')
c = conn.cursor()
c.execute("UPDATE users SET role='student' WHERE role='teacher'")
conn.commit()
conn.close()
print('DB Updated')
