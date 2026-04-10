# init_db.py
from database import init_db, add_user

if __name__ == "__main__":
    # Initialize database
    init_db()

    # Create sample users (you can change usernames and passwords later)
    add_user("admin", "admin123", role="admin", subject="None")   # Admin has no subject
    add_user("student1", "student123", role="student", subject="Math")  # Student with subject Math
    add_user("user", "password", role="student", subject="General")  # Basic demo user

    print("Database initialized and sample users added:")
    print("   - Admin -> username: admin | password: admin123 | role: admin")
    print("   - Student -> username: student1 | password: student123 | role: student (Math)")
    print("   - User -> username: user | password: password | role: student (General)")
