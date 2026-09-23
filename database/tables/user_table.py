from database.db import cursor,conn

def create_users_table():
    create_user_table_query = """
    CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    name TEXT,
    email TEXT,
    password TEXT
    )
    """

    cursor.execute(create_user_table_query)
    conn.commit()
    # conn.close()
    print("users table created")
