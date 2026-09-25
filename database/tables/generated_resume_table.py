from database.db import engine,text
def create__generated_resume_table():
    query = text("""
    CREATE TABLE IF NOT EXISTS generated_resumes (
    new_resume_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    resume_id INTEGER,
    latex_code TEXT,
    created_at TEXT,

    FOREIGN KEY (resume_id) REFERENCES resume(resume_id)
    )
    """)
    with engine.begin() as conn:
        conn.execute(query)
    print("generated_resumes table created")
