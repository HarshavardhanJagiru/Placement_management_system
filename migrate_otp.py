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
        print("Adding OTP columns to users table...")
        
        # Add is_verified safely
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN is_verified BOOLEAN DEFAULT FALSE")
            print("Added is_verified column.")
        except pymysql.err.OperationalError as e:
            if "Duplicate column" in str(e):
                print("is_verified already exists.")
            else:
                raise e

        # Add otp_code safely 
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN otp_code VARCHAR(6) DEFAULT NULL")
            print("Added otp_code column.")
        except pymysql.err.OperationalError as e:
            if "Duplicate column" in str(e):
                print("otp_code already exists.")
            else:
                raise e
                
        # Add otp_expiry safely
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN otp_expiry DATETIME DEFAULT NULL")
            print("Added otp_expiry column.")
        except pymysql.err.OperationalError as e:
            if "Duplicate column" in str(e):
                print("otp_expiry already exists.")
            else:
                raise e
        
        # For existing admins, automatically verify them
        cursor.execute("UPDATE users SET is_verified = TRUE WHERE role = 'admin'")
        # Might as well verify existing students too so we don't lock the user out of their test accounts
        cursor.execute("UPDATE users SET is_verified = TRUE WHERE role = 'student'")
        
        connection.commit()
    print("Database OTP migration completed successfully!")
except Exception as e:
    print(f"Error during OTP migration: {e}")
finally:
    if 'connection' in locals():
        connection.close()
