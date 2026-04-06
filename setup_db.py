import os
import mysql.connector

def run_sql_file(cursor, filename):
    print(f"Running {filename}...")
    with open(filename, 'r', encoding='utf-8') as f:
        sql_file = f.read()

    # MySQL allows multiple statements if executed properly, 
    # but the easiest way in Python is to split by the delimiter
    # For schema, splitting by ';' works well. 
    # For functions/procedures, we use 'DELIMITER $$' in the files.
    
    if "DELIMITER $$" in sql_file:
        statements = sql_file.split("$$")
        for statement in statements:
            stmt = statement.strip().replace("DELIMITER ;", "").replace("DELIMITER", "")
            if stmt:
                cursor.execute(stmt)
    else:
        # Standard schema split
        statements = sql_file.split(';')
        for statement in statements:
            if statement.strip():
                cursor.execute(statement)

def main():
    # Prompt for your password securely in the terminal
    import getpass
    pwd = getpass.getpass("Enter your MySQL root password (leave blank if none): ")

    try:
        # 1. Connect without database to create it
        print("\nConnecting to MySQL...")
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password=pwd,
            autocommit=True
        )
        cursor = conn.cursor()
        
        print("Creating 'nba_predictions' database...")
        cursor.execute("DROP DATABASE IF EXISTS nba_predictions;")
        cursor.execute("CREATE DATABASE nba_predictions CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
        cursor.execute("USE nba_predictions;")

        # 2. Run the SQL files in order
        run_sql_file(cursor, "sql/schema.sql")
        run_sql_file(cursor, "sql/functions.sql")
        run_sql_file(cursor, "sql/procedures.sql")

        cursor.close()
        conn.close()
        print("\n✅ Successfully created the database and ran all SQL files!")

    except mysql.connector.Error as err:
        print(f"\n❌ MySQL Error: {err}")
        print("Make sure your server is running and the password is correct.")

if __name__ == "__main__":
    main()
