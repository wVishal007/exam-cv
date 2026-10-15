from database.migrations.schema_tables.schema_tables import (
    create_users_table,
    create_resume_templates_table,
    create_llm_models_table,
    create_resume_table,
    create_candidate_profiles_table,
    create_job_descriptions_table,
    create_prompt_versions_table,
    create_analysis_runs_table,
    create_workflow_steps_table,
    create_llm_requests_table,
    create_generated_resumes_table,
    alter_generated_resumes_add_pdf_data,
    create_resume_analysis_table,
    create_resume_analysis_scores_table,
    create_analysis_feedback_items_table,
    create_resume_version_table,
    create_auth_sessions_table,
)


def create_all_tables():
    create_users_table()
    create_resume_templates_table()
    create_llm_models_table()
    create_resume_table()
    create_candidate_profiles_table()
    create_job_descriptions_table()
    create_prompt_versions_table()
    create_analysis_runs_table()
    create_workflow_steps_table()
    create_llm_requests_table()
    create_generated_resumes_table()
    alter_generated_resumes_add_pdf_data()
    create_resume_analysis_table()
    create_resume_analysis_scores_table()
    create_analysis_feedback_items_table()
    create_resume_version_table()
    create_auth_sessions_table()

