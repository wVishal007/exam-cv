from database.db import engine, text


def create_analysis(
    resume_id: int,
    model_id: int,
    feedback: str,
    suggestions: str,
    ats_score: int,
    job_vs_resume_analysis: str,
    analysis_match_score: int,
):
    query = text("""
        INSERT INTO resume_analysis (
            resume_id,
            model_id,
            ats_score,
            feedback,
            suggestions,
            analysis_match_score,
            job_vs_resume_analysis
        )
        VALUES (
            :resume_id,
            :model_id,
            :ats_score,
            :feedback,
            :suggestions,
            :analysis_match_score,
            :job_vs_resume_analysis
        )
    """)

    with engine.begin() as conn:
        conn.execute(query, {
            "resume_id": resume_id,
            "model_id": model_id,
            "ats_score": ats_score,
            "feedback": feedback,
            "suggestions": suggestions,
            "analysis_match_score": analysis_match_score,
            "job_vs_resume_analysis": job_vs_resume_analysis,
        })

def get_analysis_history(user_id: int):
    query = text("""
        SELECT
            r.resume_id,
            r.file_name,
            r.created_at AS resume_created_at,

            a.ats_score,
            a.created_at AS analysis_created_at,
            a.feedback,
            a.suggestions,
            a.analysis_match_score,
            a.job_vs_resume_analysis

        FROM resume_analysis a

        INNER JOIN resumes r
            ON a.resume_id = r.resume_id

        WHERE r.user_id = :user_id

        ORDER BY a.created_at DESC
    """)

    with engine.begin() as conn:
        result = conn.execute(query, {"user_id": user_id})
        return result.mappings().all()