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
        print("Adding skills support for ATS Job Matching...")
        
        # Add skills column to students
        try:
            cursor.execute("ALTER TABLE students ADD COLUMN skills TEXT")
            print("Added skills column to students.")
        except pymysql.err.OperationalError as e:
            if "Duplicate column" in str(e):
                print("Skills column already exists in students.")
            else:
                raise e

        # Add skills column to jobs
        try:
            cursor.execute("ALTER TABLE jobs ADD COLUMN required_skills TEXT")
            print("Added required_skills column to jobs.")
        except pymysql.err.OperationalError as e:
            if "Duplicate column" in str(e):
                print("required_skills column already exists in jobs.")
            else:
                raise e
        
        connection.commit()
    print("ATS Database migration completed successfully!")
except Exception as e:
    print(f"Error during ATS migration: {e}")
finally:
    if 'connection' in locals():
        connection.close()
