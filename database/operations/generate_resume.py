from database.db import engine, text


def save_generated_resume(
    resume_id: int,
    template_id: int,
    model_id: int,
    latex_code: str,
    preview_img_url: str,
):
    query = text("""
        INSERT INTO generated_resumes (
            resume_id,
            template_id,
            model_id,
            latex_code,
            preview_img_url
        )
        VALUES (
            :resume_id,
            :template_id,
            :model_id,
            :latex_code,
            :preview_img_url
        )
        RETURNING new_resume_id
    """)

    with engine.begin() as conn:
        result = conn.execute(
            query,
            {
                "resume_id": resume_id,
                "template_id": template_id,
                "model_id": model_id,
                "latex_code": latex_code,
                "preview_img_url": preview_img_url,
            },
        )

        return result.scalar_one()

def get_rewrite_history(user_id: int):
    query = text("""
        SELECT
            g.new_resume_id,
            g.resume_id,
            g.preview_img_url,
            g.created_at AS generated_created_at,

            r.file_name,
            r.created_at AS resume_created_at,

            t.template_id,
            t.name AS template_name,
            t.preview_img,

            a.ats_score,
            a.created_at AS analysis_created_at,
            a.feedback,
            a.suggestions,
            a.analysis_match_score,
            a.job_vs_resume_analysis

        FROM generated_resumes g

        INNER JOIN resumes r
            ON g.resume_id = r.resume_id

        LEFT JOIN resume_templates t
            ON g.template_id = t.template_id

        LEFT JOIN LATERAL (
            SELECT
                ats_score,
                created_at,
                feedback,
                suggestions,
                analysis_match_score,
                job_vs_resume_analysis
            FROM resume_analysis
            WHERE resume_analysis.resume_id = r.resume_id
            ORDER BY created_at DESC
            LIMIT 1
        ) a ON TRUE

        WHERE r.user_id = :user_id

        ORDER BY g.created_at DESC
    """)

    with engine.begin() as conn:
        result = conn.execute(query, {"user_id": user_id})
        return result.mappings().all()