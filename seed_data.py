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
        # Create an admin user (username: admin, password: admin123)
        cursor.execute("INSERT IGNORE INTO users (username, password, role, email) VALUES (%s, %s, %s, %s)", 
                     ('admin', 'admin123', 'admin', 'admin@example.com'))
        
        # Add a sample job
        cursor.execute("INSERT INTO jobs (company_name, position, salary, deadline, description) VALUES (%s, %s, %s, %s, %s)", 
                     ('Google', 'Software Engineer', '$150,000', '2026-12-31', 'Developing world-class software solutions.'))
        
        connection.commit()
    print("Admin user and sample job added successfully!")
except Exception as e:
    print(f"Error: {e}")
finally:
    if 'connection' in locals():
        connection.close()
