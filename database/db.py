import sqlite3

conn = sqlite3.connect("resume_agent.db")
cursor = conn.cursor()

print("sqlite db started")

query = "SELECT sqlite_version()"
cursor.execute(query)

result = cursor.fetchone()

print(f"sqlite version is {result[0]}")