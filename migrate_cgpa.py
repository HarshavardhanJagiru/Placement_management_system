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
        print("Adding min_cgpa column to jobs table...")
        try:
            cursor.execute("ALTER TABLE jobs ADD COLUMN min_cgpa DECIMAL(3, 2) DEFAULT 0.00")
            print("Added min_cgpa column.")
        except pymysql.err.OperationalError as e:
            if "Duplicate column" in str(e):
                print("min_cgpa already exists.")
            else:
                raise e
        connection.commit()
    print("CGPA migration completed!")
except Exception as e:
    print(f"Error: {e}")
finally:
    if 'connection' in locals():
        connection.close()
