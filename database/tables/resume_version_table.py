from database.db import cursor,conn

def create_resume_version_table():
    create_resume_version_table_query = """
    CREATE TABLE IF NOT EXISTS resume_version (
    version INTEGER PRIMARY KEY,
    resume_id INTEGER,
    ats_score INTEGER,
    created_at TEXT,

    FOREIGN KEY (resume_id) REFERENCES resume(resume_id)
    )
    """
    cursor.execute(create_resume_version_table_query)
    conn.commit()
    # conn.close()
    print("users table created")
