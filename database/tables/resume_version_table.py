from database.db import engine,text
def create_resume_version_table():
    query = text("""
    CREATE TABLE IF NOT EXISTS resume_version (
    version_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    resume_id INTEGER,
    ats_score INTEGER,
    created_at TEXT,

    FOREIGN KEY (resume_id) REFERENCES resume(resume_id)
    )
    """)
    with engine.begin() as conn:
        conn.execute(query)
    print("resume_version table created")
