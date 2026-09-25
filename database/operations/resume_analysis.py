from database.db import engine, text


def create_analysis(
    resume_id: int,
    feedback: str,
    suggestions: str,
    ats_score: int,
    job_vs_resume_analysis: str,
    analysis_match_score: int,
):
    query = text(
        """
INSERT INTO resume_analysis 
    (
    resume_id,
    ats_score,
    feedback,
    suggestions) VALUES (
        :resume_id,
        :ats_score,
        :feedback,
        :suggestions)
"""
    )
    with engine.begin() as conn:
        conn.execute(query,{
            "resume_id": resume_id,
            "feedback": feedback,
            "suggestions": suggestions,
            "ats_score": ats_score,
            "job_vs_resume_analysis": job_vs_resume_analysis,
            "analysis_match_score": analysis_match_score,
        })

