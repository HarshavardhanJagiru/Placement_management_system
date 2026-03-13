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
        print("Creating notifications table...")
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notifications (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                message TEXT NOT NULL,
                is_read BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        
        connection.commit()
    print("Notifications table created successfully!")
except Exception as e:
    print(f"Error during notifications migration: {e}")
finally:
    if 'connection' in locals():
        connection.close()
