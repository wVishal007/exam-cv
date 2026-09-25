from database.db import engine,text
def create_users_table():
    query = text("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            name TEXT,
            email TEXT,
            password TEXT
        )
    """)

    with engine.begin() as conn:
        conn.execute(query)
    print("users table created")