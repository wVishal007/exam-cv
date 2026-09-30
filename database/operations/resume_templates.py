from database.db import engine, text

def get_templates():
    query = text("""
    SELECT template_id,preview_img,name FROM resume_templates
    """)
    with engine.begin() as conn:
        result = conn.execute(query)
        return result.mappings().all()
