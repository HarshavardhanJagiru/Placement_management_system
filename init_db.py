import pymysql

db_config = {
    'host': 'localhost',
    'user': 'Harsha',
    'password': 'Harsha0218!',
}

try:
    connection = pymysql.connect(**db_config)
    with connection.cursor() as cursor:
        with open('d:/PlacementManagementSystem/sql/schema.sql', 'r') as f:
            sql_script = f.read()
            # Split by semicolon to execute multiple statements
            for statement in sql_script.split(';'):
                if statement.strip():
                    cursor.execute(statement)
        connection.commit()
    print("Database and tables created successfully!")
except Exception as e:
    print(f"Error: {e}")
finally:
    if 'connection' in locals():
        connection.close()
