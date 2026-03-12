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
        print("Expanding ENUM status for Kanban...")
        cursor.execute("ALTER TABLE applications MODIFY COLUMN status ENUM('applied', 'interview', 'offered', 'rejected', 'saved', 'in_progress') DEFAULT 'saved'")
        
        connection.commit()
    print("Database Kanban migration completed successfully!")
except Exception as e:
    print(f"Error during Kanban migration: {e}")
finally:
    if 'connection' in locals():
        connection.close()
