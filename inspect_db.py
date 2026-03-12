import pymysql

db_config = {
    'host': 'localhost',
    'user': 'Harsha',
    'password': 'Harsha0218!',
    'database': 'placement_db',
    'cursorclass': pymysql.cursors.DictCursor
}

try:
    connection = pymysql.connect(**db_config)
    with connection.cursor() as cursor:
        print("--- Table: applications ---")
        cursor.execute("SHOW CREATE TABLE applications")
        print(cursor.fetchone()['Create Table'])
        
        print("\n--- Table: students ---")
        cursor.execute("SELECT * FROM students LIMIT 5")
        for row in cursor.fetchall():
            print(row)
            
        print("\n--- Table: users ---")
        cursor.execute("SELECT * FROM users LIMIT 5")
        for row in cursor.fetchall():
            print(row)
except Exception as e:
    print(f"Error: {e}")
finally:
    if 'connection' in locals():
        connection.close()
