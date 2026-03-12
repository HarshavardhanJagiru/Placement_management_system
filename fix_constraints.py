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
        print("Fixing foreign key constraint on applications table...")
        
        # 1. Drop the incorrect constraint
        try:
            cursor.execute("ALTER TABLE applications DROP FOREIGN KEY applications_ibfk_1")
            print("Dropped incorrect constraint (users reference).")
        except Exception as e:
            print(f"Note: Could not drop constraint (might have different name): {e}")

        # 2. Add the correct constraint pointing to students(id)
        cursor.execute("ALTER TABLE applications ADD CONSTRAINT fk_student_applications FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE")
        print("Added correct constraint (students reference).")
        
        connection.commit()
    print("Database constraint fix completed successfully!")
except Exception as e:
    print(f"Error during constraint fix: {e}")
finally:
    if 'connection' in locals():
        connection.close()
