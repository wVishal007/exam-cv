from database.db import cursor,conn

def create_resume_analysis_table():
    create_resume_analysis_table_query = """
    CREATE TABLE IF NOT EXISTS resume_analysis (
    analysis_id INTEGER PRIMARY KEY,
    resume_id INTEGER,
    ats_score INTEGER,
    feedback TEXT,
    suggestions TEXT,
    created_at TEXT,

    FOREIGN KEY (resume_id) REFERENCES resume(resume_id)
    )
    """
    cursor.execute(create_resume_analysis_table_query)
    conn.commit()
    # conn.close()
    print("users table created")
