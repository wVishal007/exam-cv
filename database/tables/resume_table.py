from database.db import engine,text
def create_resume_table():
    query = text("""
    CREATE TABLE IF NOT EXISTS resume (
    resume_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id INTEGER,
    raw_text TEXT,
    file_name TEXT,
    created_at TEXT,

    FOREIGN KEY (user_id) REFERENCES users(user_id)
    )
    """)
    with engine.begin() as conn:
        conn.execute(query)
    print("resume table created")
