from database.db import cursor,conn

def create_resume_table():
    create_resume_table_query = """
    CREATE TABLE IF NOT EXISTS resume (
    resume_id INTEGER PRIMARY KEY,
    user_id INTEGER,
    raw_text TEXT,
    latex_code TEXT,
    file_name TEXT,
    created_at TEXT,

    FOREIGN KEY (user_id) REFERENCES users(user_id)
    )
    """
    cursor.execute(create_resume_table_query)
    conn.commit()
    # conn.close()
    print("users table created")
