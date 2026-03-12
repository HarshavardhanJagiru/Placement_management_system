import pymysql

db_config = {
    'host': 'localhost',
    'user': 'Harsha',
    'password': 'Harsha0218!',
    'database': 'placement_db'
}

try:
    connection = pymysql.connect(**db_config)
    with connection.cursor() as cursor:
        print("Adding interview_date column...")
        try:
            cursor.execute("ALTER TABLE applications ADD COLUMN interview_date DATETIME DEFAULT NULL")
        except Exception as e:
            print(f"Column might exist: {e}")

        print("Expanding ENUM status...")
        cursor.execute("ALTER TABLE applications MODIFY COLUMN status ENUM('pending', 'accepted', 'rejected', 'applied', 'interview', 'offered') DEFAULT 'applied'")
        
        print("Updating existing rows...")
        cursor.execute("UPDATE applications SET status='applied' WHERE status='pending'")
        cursor.execute("UPDATE applications SET status='offered' WHERE status='accepted'")
        
        print("Finalizing ENUM status...")
        cursor.execute("ALTER TABLE applications MODIFY COLUMN status ENUM('applied', 'interview', 'offered', 'rejected') DEFAULT 'applied'")
        
        connection.commit()
    print("Database migration completed successfully!")
except Exception as e:
    print(f"Error during migration: {e}")
finally:
    if 'connection' in locals():
        connection.close()
