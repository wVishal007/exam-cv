from database.db import engine, text


def upload_resume(user_id: int, raw_text: str, file_name: str):
    query = text(
        """
INSERT INTO resume (user_id,raw_text,file_name) VALUES (:user_id,:raw_text,:file_name)
RETURNING resume_id
"""
    )
    with engine.begin() as conn:
        result = conn.execute(
            query, {"user_id": user_id, "raw_text": raw_text, "file_name": file_name}
        )
        return result.scalar_one()
