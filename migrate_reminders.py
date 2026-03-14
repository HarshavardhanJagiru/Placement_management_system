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
        print("Adding reminder_sent column to applications table...")
        try:
            cursor.execute("ALTER TABLE applications ADD COLUMN reminder_sent BOOLEAN DEFAULT FALSE")
            print("Added reminder_sent column.")
        except pymysql.err.OperationalError as e:
            if "Duplicate column" in str(e):
                print("reminder_sent already exists.")
            else:
                raise e
        connection.commit()
    print("Reminder migration completed!")
except Exception as e:
    print(f"Error: {e}")
finally:
    if 'connection' in locals():
        connection.close()
