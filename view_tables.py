import sqlite3
import pandas as pd
import os

# Check if database exists
if not os.path.exists('naics.db'):
    print("❌ naics.db does not exist. Please run load_naics.py first.")
    exit(1)

# Connect to the database
conn = sqlite3.connect('naics.db')
cursor = conn.cursor()

# Get list of tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = [table[0] for table in cursor.fetchall()]

if not tables:
    print("❌ No tables found in the database.")
    conn.close()
    exit(1)

print(f"📊 Found tables: {', '.join(tables)}\n")

# Query and display first 3 rows of each table
for table in tables:
    print(f"\n=== First 3 rows of {table} ===")
    try:
        query = f"SELECT * FROM {table} LIMIT 3"
        df = pd.read_sql_query(query, conn)
        if df.empty:
            print(f"⚠️ Table {table} is empty")
        else:
            print(df)
    except Exception as e:
        print(f"❌ Error querying {table}: {str(e)}")
    print("\n" + "="*50)

conn.close() 