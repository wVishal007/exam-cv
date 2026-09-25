from database.db import engine,text

def create_resume_analysis_table():
    query = text("""
    CREATE TABLE IF NOT EXISTS resume_analysis (
    analysis_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    resume_id INTEGER,
    ats_score INTEGER,
    feedback TEXT,
    suggestions TEXT,
    analysis_match_score INTEGER,
    job_vs_resume_analysis TEXT,
    created_at TEXT,

    FOREIGN KEY (resume_id) REFERENCES resume(resume_id)
    )
    """)
    with engine.begin() as conn:
        conn.execute(query)
    # conn.close()
    print("resume_analysis table created")
