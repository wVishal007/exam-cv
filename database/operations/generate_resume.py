from database.db import engine, text


def save_generated_resume(resume_id: int, latex_code: str):
    query = text(
        """
INSERT INTO generated_resumes (resume_id,latex_code) VALUES (:resume_id,:latex_code)
RETURNING resume_id
"""
    )
    with engine.begin() as conn:
        result = conn.execute(
            query, {"resume_id": resume_id, "latex_code": latex_code}
        )
        return result.scalar_one()
