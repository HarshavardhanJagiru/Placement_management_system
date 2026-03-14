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
        print("Adding resume_filename column to students table...")
        try:
            cursor.execute("ALTER TABLE students ADD COLUMN resume_filename VARCHAR(255) DEFAULT NULL")
            print("Added resume_filename column.")
        except pymysql.err.OperationalError as e:
            if "Duplicate column" in str(e):
                print("resume_filename already exists.")
            else:
                raise e
        connection.commit()
    print("Resume migration completed!")
except Exception as e:
    print(f"Error: {e}")
finally:
    if 'connection' in locals():
        connection.close()
