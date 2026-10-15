from database.db import engine, text


def create_users_table():
    query = text("""
        CREATE TABLE IF NOT EXISTS users (
            user_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            name TEXT,
            email TEXT UNIQUE,
            password TEXT
        )
    """)
    with engine.begin() as conn:
        conn.execute(query)
    print("users table created")


def create_resume_templates_table():
    query = text("""
        CREATE TABLE IF NOT EXISTS resume_templates (
            template_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            template_key TEXT,
            preview_img TEXT,
            name TEXT,
            version TEXT,
            style_metadata JSONB,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)
    with engine.begin() as conn:
        conn.execute(query)
    print("resume_templates table created")


def create_llm_models_table():
    query = text("""
        CREATE TABLE IF NOT EXISTS llm_models (
            model_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            provider TEXT NOT NULL,
            name TEXT NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
            UNIQUE (provider, name)
        )
    """)
    with engine.begin() as conn:
        conn.execute(query)
    print("llm_models table created")


def create_resume_table():
    query = text("""
        CREATE TABLE IF NOT EXISTS resumes (
            resume_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            user_id BIGINT,
            raw_text TEXT,
            file_name TEXT,
            created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    """)
    with engine.begin() as conn:
        conn.execute(query)
    print("resume table created")


def create_candidate_profiles_table():
    query = text("""
        CREATE TABLE IF NOT EXISTS candidate_profiles (
            profile_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            user_id BIGINT,
            source_resume_id BIGINT,
            profile_json JSONB,
            profile_version INTEGER,
            content_hash TEXT,
            created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            FOREIGN KEY (source_resume_id) REFERENCES resumes(resume_id)
        )
    """)
    with engine.begin() as conn:
        conn.execute(query)
    print("candidate_profiles table created")


def create_job_descriptions_table():
    query = text("""
        CREATE TABLE IF NOT EXISTS job_descriptions (
            job_description_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            user_id BIGINT,
            title TEXT,
            company TEXT,
            raw_text TEXT,
            source_url TEXT,
            location TEXT,
            created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMPTZ,
            is_archived BOOLEAN DEFAULT FALSE,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    """)
    with engine.begin() as conn:
        conn.execute(query)
    print("job_descriptions table created")


def create_prompt_versions_table():
    query = text("""
        CREATE TABLE IF NOT EXISTS prompt_versions (
            prompt_version_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            prompt_key TEXT NOT NULL,
            version TEXT NOT NULL,
            prompt_text TEXT NOT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
            UNIQUE (prompt_key, version)
        )
    """)
    with engine.begin() as conn:
        conn.execute(query)
    print("prompt_versions table created")


def create_analysis_runs_table():
    query = text("""
        CREATE TABLE IF NOT EXISTS analysis_runs (
            run_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            user_id BIGINT,
            resume_id BIGINT,
            job_description_id BIGINT,
            run_type TEXT,
            status TEXT,
            progress_percent INTEGER,
            requested_template TEXT,
            error_message TEXT,
            started_at TIMESTAMPTZ,
            completed_at TIMESTAMPTZ,
            created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            FOREIGN KEY (resume_id) REFERENCES resumes(resume_id),
            FOREIGN KEY (job_description_id)
                REFERENCES job_descriptions(job_description_id)
        )
    """)
    with engine.begin() as conn:
        conn.execute(query)
    print("analysis_runs table created")


def create_workflow_steps_table():
    query = text("""
        CREATE TABLE IF NOT EXISTS workflow_steps (
            step_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            run_id BIGINT,
            node_name TEXT,
            attempt_number INTEGER,
            status TEXT,
            input_ref JSONB,
            output_ref JSONB,
            error_message TEXT,
            started_at TIMESTAMPTZ,
            completed_at TIMESTAMPTZ,
            FOREIGN KEY (run_id) REFERENCES analysis_runs(run_id)
        )
    """)
    with engine.begin() as conn:
        conn.execute(query)
    print("workflow_steps table created")


def create_llm_requests_table():
    query = text("""
        CREATE TABLE IF NOT EXISTS llm_requests (
            request_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            run_id BIGINT,
            step_id BIGINT,
            provider TEXT,
            model_name TEXT,
            prompt_version_id BIGINT,
            input_tokens INTEGER,
            output_tokens INTEGER,
            latency_ms INTEGER,
            estimated_cost NUMERIC(12, 6),
            status TEXT,
            error_message TEXT,
            created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (run_id) REFERENCES analysis_runs(run_id),
            FOREIGN KEY (step_id) REFERENCES workflow_steps(step_id),
            FOREIGN KEY (prompt_version_id)
                REFERENCES prompt_versions(prompt_version_id)
        )
    """)
    with engine.begin() as conn:
        conn.execute(query)
    print("llm_requests table created")


def create_generated_resumes_table():
    query = text("""
        CREATE TABLE IF NOT EXISTS generated_resumes (
            new_resume_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            resume_id BIGINT,
            template_id BIGINT,
            template_version TEXT,
            latex_code TEXT,
            preview_img_url TEXT,
            created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
            model_id INTEGER,
            profile_id BIGINT,
            prompt_version_id BIGINT,
            pdf_storage_key TEXT,
            pdf_data BYTEA,
            validation_status TEXT,
            page_count INTEGER,
            factuality_status TEXT,
            FOREIGN KEY (resume_id) REFERENCES resumes(resume_id),
            FOREIGN KEY (template_id) REFERENCES resume_templates(template_id),
            FOREIGN KEY (model_id) REFERENCES llm_models(model_id),
            FOREIGN KEY (profile_id) REFERENCES candidate_profiles(profile_id),
            FOREIGN KEY (prompt_version_id)
                REFERENCES prompt_versions(prompt_version_id)
        )
    """)
    with engine.begin() as conn:
        conn.execute(query)
    print("generated_resumes table created")


def alter_generated_resumes_add_pdf_data():
    query = text("""
        ALTER TABLE generated_resumes
        ADD COLUMN IF NOT EXISTS pdf_data BYTEA
    """)
    with engine.begin() as conn:
        conn.execute(query)
    print("generated_resumes.pdf_data column ensured")


def create_resume_analysis_table():
    query = text("""
        CREATE TABLE IF NOT EXISTS resume_analysis (
            analysis_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            resume_id BIGINT,
            ats_score INTEGER,
            feedback TEXT,
            model_id INTEGER,
            suggestions TEXT,
            analysis_match_score INTEGER,
            job_vs_resume_analysis TEXT,
            created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
            run_id BIGINT,
            FOREIGN KEY (resume_id) REFERENCES resumes(resume_id),
            FOREIGN KEY (model_id) REFERENCES llm_models(model_id),
            FOREIGN KEY (run_id) REFERENCES analysis_runs(run_id)
        )
    """)
    with engine.begin() as conn:
        conn.execute(query)
    print("resume_analysis table created")


def create_resume_analysis_scores_table():
    query = text("""
        CREATE TABLE IF NOT EXISTS resume_analysis_scores (
            score_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            analysis_id BIGINT,
            dimension TEXT,
            score INTEGER,
            weight NUMERIC(5, 2),
            feedback TEXT,
            FOREIGN KEY (analysis_id)
                REFERENCES resume_analysis(analysis_id)
        )
    """)
    with engine.begin() as conn:
        conn.execute(query)
    print("resume_analysis_scores table created")


def create_analysis_feedback_items_table():
    query = text("""
        CREATE TABLE IF NOT EXISTS analysis_feedback_items (
            feedback_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            analysis_id BIGINT,
            priority TEXT,
            category TEXT,
            problem TEXT,
            why_it_matters TEXT,
            recommended_fix TEXT,
            status TEXT,
            sort_order INTEGER,
            FOREIGN KEY (analysis_id)
                REFERENCES resume_analysis(analysis_id)
        )
    """)
    with engine.begin() as conn:
        conn.execute(query)
    print("analysis_feedback_items table created")


def create_resume_version_table():
    query = text("""
        CREATE TABLE IF NOT EXISTS resume_version (
            version_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            resume_id BIGINT,
            new_resume_id BIGINT,
            ats_score INTEGER,
            created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (resume_id) REFERENCES resumes(resume_id),
            FOREIGN KEY (new_resume_id)
                REFERENCES generated_resumes(new_resume_id)
        )
    """)
    with engine.begin() as conn:
        conn.execute(query)
    print("resume_version table created")


def create_auth_sessions_table():
    query = text("""
        CREATE TABLE IF NOT EXISTS auth_sessions (
            session_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            user_id BIGINT,
            token_hash TEXT NOT NULL,
            device_name TEXT,
            ip_address INET,
            user_agent TEXT,
            expires_at TIMESTAMPTZ,
            revoked_at TIMESTAMPTZ,
            created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
            last_used_at TIMESTAMPTZ,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    """)
    with engine.begin() as conn:
        conn.execute(query)
    print("auth_sessions table created")
