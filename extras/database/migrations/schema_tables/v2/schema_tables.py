# # -- ============================================================
# # -- RESUME AI SAAS DATABASE
# # -- PostgreSQL
# # -- Complete schema:
# # --   Authentication
# # --   Multi-tenancy / Organizations
# # --   Resume Management
# # --   Job Descriptions
# # --   AI Analysis
# # --   LangGraph Workflow Tracking
# # --   LLM Tracking
# # --   Resume Generation
# # --   SaaS Plans
# # --   Billing
# # --   Payments
# # --   Invoices
# # --   Refunds
# # --   Webhooks
# # --   Usage Metering
# # --   Credits
# # -- ============================================================


# # -- ============================================================
# # -- 1. USERS
# # -- ============================================================

# CREATE TABLE IF NOT EXISTS users (
#     user_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

#     name TEXT,
#     email TEXT NOT NULL UNIQUE,
#     password TEXT,

#     created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
#     updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
# );


# -- ============================================================
# -- 2. AUTH SESSIONS
# -- ============================================================

# CREATE TABLE IF NOT EXISTS auth_sessions (
#     session_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

#     user_id BIGINT NOT NULL,

#     token_hash TEXT NOT NULL UNIQUE,

#     device_name TEXT,
#     ip_address INET,
#     user_agent TEXT,

#     expires_at TIMESTAMPTZ,
#     revoked_at TIMESTAMPTZ,

#     created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
#     last_used_at TIMESTAMPTZ,

#     CONSTRAINT fk_auth_sessions_user
#         FOREIGN KEY (user_id)
#         REFERENCES users(user_id)
#         ON DELETE CASCADE
# );


# -- ============================================================
# -- 3. ORGANIZATIONS / TENANTS
# -- ============================================================

# CREATE TABLE IF NOT EXISTS organizations (
#     organization_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

#     name TEXT NOT NULL,
#     slug TEXT NOT NULL UNIQUE,

#     created_by_user_id BIGINT NOT NULL,

#     created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

#     is_active BOOLEAN NOT NULL DEFAULT TRUE,

#     CONSTRAINT fk_organizations_creator
#         FOREIGN KEY (created_by_user_id)
#         REFERENCES users(user_id)
#         ON DELETE RESTRICT
# );


# -- ============================================================
# -- 4. ORGANIZATION MEMBERS
# -- ============================================================

# CREATE TABLE IF NOT EXISTS organization_members (
#     membership_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

#     organization_id BIGINT NOT NULL,
#     user_id BIGINT NOT NULL,

#     role TEXT NOT NULL DEFAULT 'member',

#     joined_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

#     status TEXT NOT NULL DEFAULT 'active',

#     CONSTRAINT fk_org_members_organization
#         FOREIGN KEY (organization_id)
#         REFERENCES organizations(organization_id)
#         ON DELETE CASCADE,

#     CONSTRAINT fk_org_members_user
#         FOREIGN KEY (user_id)
#         REFERENCES users(user_id)
#         ON DELETE CASCADE,

#     CONSTRAINT uq_org_member
#         UNIQUE (organization_id, user_id),

#     CONSTRAINT chk_org_member_role
#         CHECK (role IN ('owner', 'admin', 'member', 'viewer')),

#     CONSTRAINT chk_org_member_status
#         CHECK (status IN ('active', 'invited', 'suspended'))
# );


# -- ============================================================
# -- 5. RESUME TEMPLATES
# -- ============================================================

# CREATE TABLE IF NOT EXISTS resume_templates (
#     template_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

#     template_key TEXT NOT NULL,

#     preview_img TEXT,

#     name TEXT NOT NULL,

#     version TEXT NOT NULL,

#     style_metadata JSONB,

#     is_active BOOLEAN NOT NULL DEFAULT TRUE,

#     created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
#     updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

#     CONSTRAINT uq_resume_template_version
#         UNIQUE (template_key, version)
# );


# -- ============================================================
# -- 6. LLM MODELS
# -- ============================================================

# CREATE TABLE IF NOT EXISTS llm_models (
#     model_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

#     provider TEXT NOT NULL,
#     name TEXT NOT NULL,

#     created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

#     CONSTRAINT uq_llm_provider_model
#         UNIQUE (provider, name)
# );


# -- ============================================================
# -- 7. RESUMES
# -- ============================================================

# CREATE TABLE IF NOT EXISTS resumes (
#     resume_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

#     user_id BIGINT NOT NULL,

#     -- Optional tenant ownership.
#     -- Personal users can have this NULL.
#     organization_id BIGINT,

#     raw_text TEXT,
#     file_name TEXT,

#     created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

#     CONSTRAINT fk_resumes_user
#         FOREIGN KEY (user_id)
#         REFERENCES users(user_id)
#         ON DELETE CASCADE,

#     CONSTRAINT fk_resumes_organization
#         FOREIGN KEY (organization_id)
#         REFERENCES organizations(organization_id)
#         ON DELETE SET NULL
# );


# -- ============================================================
# -- 8. CANDIDATE PROFILES
# -- ============================================================

# CREATE TABLE IF NOT EXISTS candidate_profiles (
#     profile_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

#     user_id BIGINT NOT NULL,

#     source_resume_id BIGINT,

#     profile_json JSONB,

#     profile_version INTEGER NOT NULL DEFAULT 1,

#     content_hash TEXT,

#     created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

#     CONSTRAINT fk_candidate_profiles_user
#         FOREIGN KEY (user_id)
#         REFERENCES users(user_id)
#         ON DELETE CASCADE,

#     CONSTRAINT fk_candidate_profiles_resume
#         FOREIGN KEY (source_resume_id)
#         REFERENCES resumes(resume_id)
#         ON DELETE SET NULL
# );


# -- ============================================================
# -- 9. JOB DESCRIPTIONS
# -- ============================================================

# CREATE TABLE IF NOT EXISTS job_descriptions (
#     job_description_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

#     user_id BIGINT NOT NULL,

#     organization_id BIGINT,

#     title TEXT,
#     company TEXT,

#     raw_text TEXT,

#     source_url TEXT,

#     location TEXT,

#     created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
#     updated_at TIMESTAMPTZ,

#     is_archived BOOLEAN NOT NULL DEFAULT FALSE,

#     CONSTRAINT fk_job_descriptions_user
#         FOREIGN KEY (user_id)
#         REFERENCES users(user_id)
#         ON DELETE CASCADE,

#     CONSTRAINT fk_job_descriptions_organization
#         FOREIGN KEY (organization_id)
#         REFERENCES organizations(organization_id)
#         ON DELETE SET NULL
# );


# -- ============================================================
# -- 10. PROMPT VERSIONS
# -- ============================================================

# CREATE TABLE IF NOT EXISTS prompt_versions (
#     prompt_version_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

#     prompt_key TEXT NOT NULL,

#     version TEXT NOT NULL,

#     prompt_text TEXT NOT NULL,

#     is_active BOOLEAN NOT NULL DEFAULT TRUE,

#     created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

#     CONSTRAINT uq_prompt_version
#         UNIQUE (prompt_key, version)
# );


# -- ============================================================
# -- 11. ANALYSIS RUNS
# -- ============================================================

# CREATE TABLE IF NOT EXISTS analysis_runs (
#     run_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

#     user_id BIGINT NOT NULL,

#     organization_id BIGINT,

#     resume_id BIGINT,

#     job_description_id BIGINT,

#     run_type TEXT NOT NULL,

#     status TEXT NOT NULL DEFAULT 'queued',

#     progress_percent INTEGER NOT NULL DEFAULT 0,

#     requested_template TEXT,

#     error_message TEXT,

#     started_at TIMESTAMPTZ,
#     completed_at TIMESTAMPTZ,

#     created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

#     CONSTRAINT fk_analysis_runs_user
#         FOREIGN KEY (user_id)
#         REFERENCES users(user_id)
#         ON DELETE CASCADE,

#     CONSTRAINT fk_analysis_runs_organization
#         FOREIGN KEY (organization_id)
#         REFERENCES organizations(organization_id)
#         ON DELETE SET NULL,

#     CONSTRAINT fk_analysis_runs_resume
#         FOREIGN KEY (resume_id)
#         REFERENCES resumes(resume_id)
#         ON DELETE SET NULL,

#     CONSTRAINT fk_analysis_runs_job
#         FOREIGN KEY (job_description_id)
#         REFERENCES job_descriptions(job_description_id)
#         ON DELETE SET NULL,

#     CONSTRAINT chk_analysis_progress
#         CHECK (progress_percent BETWEEN 0 AND 100)
# );


# -- ============================================================
# -- 12. WORKFLOW STEPS
# -- ============================================================

# CREATE TABLE IF NOT EXISTS workflow_steps (
#     step_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

#     run_id BIGINT NOT NULL,

#     node_name TEXT NOT NULL,

#     attempt_number INTEGER NOT NULL DEFAULT 1,

#     status TEXT NOT NULL,

#     input_ref JSONB,

#     output_ref JSONB,

#     error_message TEXT,

#     started_at TIMESTAMPTZ,
#     completed_at TIMESTAMPTZ,

#     CONSTRAINT fk_workflow_steps_run
#         FOREIGN KEY (run_id)
#         REFERENCES analysis_runs(run_id)
#         ON DELETE CASCADE,

#     CONSTRAINT chk_workflow_attempt
#         CHECK (attempt_number >= 1)
# );


# -- ============================================================
# -- 13. LLM REQUESTS
# -- ============================================================

# CREATE TABLE IF NOT EXISTS llm_requests (
#     request_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

#     run_id BIGINT,

#     step_id BIGINT,

#     provider TEXT,

#     model_name TEXT,

#     prompt_version_id BIGINT,

#     input_tokens INTEGER,
#     output_tokens INTEGER,

#     latency_ms INTEGER,

#     estimated_cost NUMERIC(12, 6),

#     status TEXT,

#     error_message TEXT,

#     created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

#     CONSTRAINT fk_llm_requests_run
#         FOREIGN KEY (run_id)
#         REFERENCES analysis_runs(run_id)
#         ON DELETE SET NULL,

#     CONSTRAINT fk_llm_requests_step
#         FOREIGN KEY (step_id)
#         REFERENCES workflow_steps(step_id)
#         ON DELETE SET NULL,

#     CONSTRAINT fk_llm_requests_prompt
#         FOREIGN KEY (prompt_version_id)
#         REFERENCES prompt_versions(prompt_version_id)
#         ON DELETE SET NULL,

#     CONSTRAINT chk_llm_cost
#         CHECK (estimated_cost IS NULL OR estimated_cost >= 0),

#     CONSTRAINT chk_llm_latency
#         CHECK (latency_ms IS NULL OR latency_ms >= 0)
# );


# -- ============================================================
# -- 14. GENERATED RESUMES
# -- ============================================================

# CREATE TABLE IF NOT EXISTS generated_resumes (
#     new_resume_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

#     resume_id BIGINT,

#     template_id BIGINT,

#     template_version TEXT,

#     latex_code TEXT,

#     preview_img_url TEXT,

#     created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

#     model_id INTEGER,

#     profile_id BIGINT,

#     prompt_version_id BIGINT,

#     pdf_storage_key TEXT,

#     pdf_data BYTEA,

#     validation_status TEXT,

#     page_count INTEGER,

#     factuality_status TEXT,

#     CONSTRAINT fk_generated_resume_source
#         FOREIGN KEY (resume_id)
#         REFERENCES resumes(resume_id)
#         ON DELETE SET NULL,

#     CONSTRAINT fk_generated_resume_template
#         FOREIGN KEY (template_id)
#         REFERENCES resume_templates(template_id)
#         ON DELETE SET NULL,

#     CONSTRAINT fk_generated_resume_model
#         FOREIGN KEY (model_id)
#         REFERENCES llm_models(model_id)
#         ON DELETE SET NULL,

#     CONSTRAINT fk_generated_resume_profile
#         FOREIGN KEY (profile_id)
#         REFERENCES candidate_profiles(profile_id)
#         ON DELETE SET NULL,

#     CONSTRAINT fk_generated_resume_prompt
#         FOREIGN KEY (prompt_version_id)
#         REFERENCES prompt_versions(prompt_version_id)
#         ON DELETE SET NULL,

#     CONSTRAINT chk_generated_page_count
#         CHECK (page_count IS NULL OR page_count > 0)
# );


# -- ============================================================
# -- 15. RESUME ANALYSIS
# -- ============================================================

# CREATE TABLE IF NOT EXISTS resume_analysis (
#     analysis_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

#     resume_id BIGINT NOT NULL,

#     ats_score INTEGER,

#     feedback TEXT,

#     model_id INTEGER,

#     suggestions TEXT,

#     analysis_match_score INTEGER,

#     job_vs_resume_analysis TEXT,

#     created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

#     run_id BIGINT,

#     CONSTRAINT fk_resume_analysis_resume
#         FOREIGN KEY (resume_id)
#         REFERENCES resumes(resume_id)
#         ON DELETE CASCADE,

#     CONSTRAINT fk_resume_analysis_model
#         FOREIGN KEY (model_id)
#         REFERENCES llm_models(model_id)
#         ON DELETE SET NULL,

#     CONSTRAINT fk_resume_analysis_run
#         FOREIGN KEY (run_id)
#         REFERENCES analysis_runs(run_id)
#         ON DELETE SET NULL,

#     CONSTRAINT chk_ats_score
#         CHECK (ats_score IS NULL OR ats_score BETWEEN 0 AND 100),

#     CONSTRAINT chk_match_score
#         CHECK (
#             analysis_match_score IS NULL
#             OR analysis_match_score BETWEEN 0 AND 100
#         )
# );


# -- ============================================================
# -- 16. RESUME ANALYSIS SCORES
# -- ============================================================

# CREATE TABLE IF NOT EXISTS resume_analysis_scores (
#     score_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

#     analysis_id BIGINT NOT NULL,

#     dimension TEXT NOT NULL,

#     score INTEGER,

#     weight NUMERIC(5, 2),

#     feedback TEXT,

#     CONSTRAINT fk_analysis_scores_analysis
#         FOREIGN KEY (analysis_id)
#         REFERENCES resume_analysis(analysis_id)
#         ON DELETE CASCADE,

#     CONSTRAINT chk_dimension_score
#         CHECK (score IS NULL OR score BETWEEN 0 AND 100),

#     CONSTRAINT chk_dimension_weight
#         CHECK (weight IS NULL OR weight >= 0),

#     CONSTRAINT uq_analysis_dimension
#         UNIQUE (analysis_id, dimension)
# );


# -- ============================================================
# -- 17. ANALYSIS FEEDBACK ITEMS
# -- ============================================================

# CREATE TABLE IF NOT EXISTS analysis_feedback_items (
#     feedback_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

#     analysis_id BIGINT NOT NULL,

#     priority TEXT,

#     category TEXT,

#     problem TEXT,

#     why_it_matters TEXT,

#     recommended_fix TEXT,

#     status TEXT,

#     sort_order INTEGER,

#     CONSTRAINT fk_feedback_analysis
#         FOREIGN KEY (analysis_id)
#         REFERENCES resume_analysis(analysis_id)
#         ON DELETE CASCADE
# );


# -- ============================================================
# -- 18. RESUME VERSIONS
# -- ============================================================

# CREATE TABLE IF NOT EXISTS resume_version (
#     version_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

#     resume_id BIGINT NOT NULL,

#     new_resume_id BIGINT,

#     ats_score INTEGER,

#     created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

#     CONSTRAINT fk_resume_version_original
#         FOREIGN KEY (resume_id)
#         REFERENCES resumes(resume_id)
#         ON DELETE CASCADE,

#     CONSTRAINT fk_resume_version_generated
#         FOREIGN KEY (new_resume_id)
#         REFERENCES generated_resumes(new_resume_id)
#         ON DELETE SET NULL,

#     CONSTRAINT chk_version_ats_score
#         CHECK (ats_score IS NULL OR ats_score BETWEEN 0 AND 100)
# );


# -- ============================================================
# -- ============================================================
# -- SAAS BILLING SYSTEM
# -- ============================================================
# -- ============================================================


# -- ============================================================
# -- 19. PLANS
# -- ============================================================

# CREATE TABLE IF NOT EXISTS plans (
#     plan_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

#     plan_key TEXT NOT NULL UNIQUE,

#     name TEXT NOT NULL,

#     description TEXT,

#     is_active BOOLEAN NOT NULL DEFAULT TRUE,

#     created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
# );


# -- ============================================================
# -- 20. PLAN PRICES
# -- ============================================================

# CREATE TABLE IF NOT EXISTS plan_prices (
#     price_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

#     plan_id BIGINT NOT NULL,

#     provider TEXT NOT NULL,

#     provider_plan_id TEXT,

#     amount NUMERIC(12, 2) NOT NULL,

#     currency TEXT NOT NULL DEFAULT 'USD',

#     billing_interval TEXT NOT NULL,

#     is_active BOOLEAN NOT NULL DEFAULT TRUE,

#     CONSTRAINT fk_plan_prices_plan
#         FOREIGN KEY (plan_id)
#         REFERENCES plans(plan_id)
#         ON DELETE CASCADE,

#     CONSTRAINT uq_provider_plan
#         UNIQUE (provider, provider_plan_id),

#     CONSTRAINT chk_plan_price_amount
#         CHECK (amount >= 0),

#     CONSTRAINT chk_billing_interval
#         CHECK (
#             billing_interval IN (
#                 'one_time',
#                 'daily',
#                 'weekly',
#                 'monthly',
#                 'yearly'
#             )
#         )
# );


# -- ============================================================
# -- 21. PLAN ENTITLEMENTS
# -- ============================================================

# CREATE TABLE IF NOT EXISTS plan_entitlements (
#     entitlement_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

#     plan_id BIGINT NOT NULL,

#     entitlement_key TEXT NOT NULL,

#     limit_value NUMERIC(12, 2),

#     unit TEXT,

#     is_active BOOLEAN NOT NULL DEFAULT TRUE,

#     CONSTRAINT fk_plan_entitlements_plan
#         FOREIGN KEY (plan_id)
#         REFERENCES plans(plan_id)
#         ON DELETE CASCADE,

#     CONSTRAINT uq_plan_entitlement
#         UNIQUE (plan_id, entitlement_key),

#     CONSTRAINT chk_entitlement_limit
#         CHECK (limit_value IS NULL OR limit_value >= 0)
# );


# -- ============================================================
# -- 22. BILLING CUSTOMERS
# -- ============================================================

# CREATE TABLE IF NOT EXISTS billing_customers (
#     billing_customer_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

#     organization_id BIGINT NOT NULL,

#     provider TEXT NOT NULL,

#     provider_customer_id TEXT NOT NULL,

#     email TEXT,

#     created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

#     CONSTRAINT fk_billing_customer_organization
#         FOREIGN KEY (organization_id)
#         REFERENCES organizations(organization_id)
#         ON DELETE CASCADE,

#     CONSTRAINT uq_billing_provider_customer
#         UNIQUE (provider, provider_customer_id),

#     CONSTRAINT uq_org_billing_provider
#         UNIQUE (organization_id, provider)
# );


# -- ============================================================
# -- 23. SUBSCRIPTIONS
# -- ============================================================

# CREATE TABLE IF NOT EXISTS subscriptions (
#     subscription_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

#     organization_id BIGINT NOT NULL,

#     plan_id BIGINT NOT NULL,

#     price_id BIGINT NOT NULL,

#     provider TEXT NOT NULL,

#     provider_subscription_id TEXT NOT NULL,

#     status TEXT NOT NULL,

#     current_period_start TIMESTAMPTZ,

#     current_period_end TIMESTAMPTZ,

#     cancel_at_period_end BOOLEAN NOT NULL DEFAULT FALSE,

#     created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

#     CONSTRAINT fk_subscription_organization
#         FOREIGN KEY (organization_id)
#         REFERENCES organizations(organization_id)
#         ON DELETE RESTRICT,

#     CONSTRAINT fk_subscription_plan
#         FOREIGN KEY (plan_id)
#         REFERENCES plans(plan_id)
#         ON DELETE RESTRICT,

#     CONSTRAINT fk_subscription_price
#         FOREIGN KEY (price_id)
#         REFERENCES plan_prices(price_id)
#         ON DELETE RESTRICT,

#     CONSTRAINT uq_provider_subscription
#         UNIQUE (provider, provider_subscription_id)
# );


# -- ============================================================
# -- 24. PAYMENT ORDERS
# -- ============================================================

# CREATE TABLE IF NOT EXISTS payment_orders (
#     order_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

#     organization_id BIGINT NOT NULL,

#     subscription_id BIGINT,

#     provider TEXT NOT NULL,

#     provider_order_id TEXT NOT NULL,

#     amount NUMERIC(12, 2) NOT NULL,

#     currency TEXT NOT NULL DEFAULT 'USD',

#     status TEXT NOT NULL,

#     created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

#     CONSTRAINT fk_payment_order_organization
#         FOREIGN KEY (organization_id)
#         REFERENCES organizations(organization_id)
#         ON DELETE RESTRICT,

#     CONSTRAINT fk_payment_order_subscription
#         FOREIGN KEY (subscription_id)
#         REFERENCES subscriptions(subscription_id)
#         ON DELETE SET NULL,

#     CONSTRAINT uq_provider_order
#         UNIQUE (provider, provider_order_id),

#     CONSTRAINT chk_payment_order_amount
#         CHECK (amount >= 0)
# );


# -- ============================================================
# -- 25. PAYMENTS
# -- ============================================================

# CREATE TABLE IF NOT EXISTS payments (
#     payment_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

#     organization_id BIGINT NOT NULL,

#     order_id BIGINT,

#     subscription_id BIGINT,

#     provider TEXT NOT NULL,

#     provider_payment_id TEXT NOT NULL,

#     amount NUMERIC(12, 2) NOT NULL,

#     currency TEXT NOT NULL DEFAULT 'USD',

#     status TEXT NOT NULL,

#     paid_at TIMESTAMPTZ,

#     CONSTRAINT fk_payment_organization
#         FOREIGN KEY (organization_id)
#         REFERENCES organizations(organization_id)
#         ON DELETE RESTRICT,

#     CONSTRAINT fk_payment_order
#         FOREIGN KEY (order_id)
#         REFERENCES payment_orders(order_id)
#         ON DELETE SET NULL,

#     CONSTRAINT fk_payment_subscription
#         FOREIGN KEY (subscription_id)
#         REFERENCES subscriptions(subscription_id)
#         ON DELETE SET NULL,

#     CONSTRAINT uq_provider_payment
#         UNIQUE (provider, provider_payment_id),

#     CONSTRAINT chk_payment_amount
#         CHECK (amount >= 0)
# );


# -- ============================================================
# -- 26. INVOICES
# -- ============================================================

# CREATE TABLE IF NOT EXISTS invoices (
#     invoice_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

#     organization_id BIGINT NOT NULL,

#     subscription_id BIGINT,

#     payment_id BIGINT,

#     provider_invoice_id TEXT,

#     invoice_number TEXT,

#     amount NUMERIC(12, 2) NOT NULL,

#     tax_amount NUMERIC(12, 2) NOT NULL DEFAULT 0,

#     currency TEXT NOT NULL DEFAULT 'USD',

#     status TEXT NOT NULL,

#     issued_at TIMESTAMPTZ,

#     due_at TIMESTAMPTZ,

#     CONSTRAINT fk_invoice_organization
#         FOREIGN KEY (organization_id)
#         REFERENCES organizations(organization_id)
#         ON DELETE RESTRICT,

#     CONSTRAINT fk_invoice_subscription
#         FOREIGN KEY (subscription_id)
#         REFERENCES subscriptions(subscription_id)
#         ON DELETE SET NULL,

#     CONSTRAINT fk_invoice_payment
#         FOREIGN KEY (payment_id)
#         REFERENCES payments(payment_id)
#         ON DELETE SET NULL,

#     CONSTRAINT uq_provider_invoice
#         UNIQUE (provider_invoice_id),

#     CONSTRAINT chk_invoice_amount
#         CHECK (amount >= 0),

#     CONSTRAINT chk_invoice_tax
#         CHECK (tax_amount >= 0)
# );


# -- ============================================================
# -- 27. REFUNDS
# -- ============================================================

# CREATE TABLE IF NOT EXISTS refunds (
#     refund_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

#     payment_id BIGINT NOT NULL,

#     provider_refund_id TEXT,

#     amount NUMERIC(12, 2) NOT NULL,

#     reason TEXT,

#     status TEXT NOT NULL,

#     created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

#     CONSTRAINT fk_refund_payment
#         FOREIGN KEY (payment_id)
#         REFERENCES payments(payment_id)
#         ON DELETE RESTRICT,

#     CONSTRAINT uq_provider_refund
#         UNIQUE (provider_refund_id),

#     CONSTRAINT chk_refund_amount
#         CHECK (amount > 0)
# );


# -- ============================================================
# -- 28. PAYMENT WEBHOOK EVENTS
# -- ============================================================

# CREATE TABLE IF NOT EXISTS payment_webhook_events (
#     webhook_event_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

#     provider TEXT NOT NULL,

#     provider_event_id TEXT NOT NULL,

#     event_type TEXT NOT NULL,

#     payload_json JSONB NOT NULL,

#     processing_status TEXT NOT NULL DEFAULT 'pending',

#     processed_at TIMESTAMPTZ,

#     created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

#     CONSTRAINT uq_provider_webhook_event
#         UNIQUE (provider, provider_event_id)
# );


# -- ============================================================
# -- ============================================================
# -- USAGE / METERING
# -- ============================================================
# -- ============================================================


# -- ============================================================
# -- 29. USAGE EVENTS
# -- ============================================================

# CREATE TABLE IF NOT EXISTS usage_events (
#     usage_event_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

#     organization_id BIGINT NOT NULL,

#     user_id BIGINT,

#     metric_key TEXT NOT NULL,

#     quantity NUMERIC(12, 2) NOT NULL,

#     source_type TEXT,

#     source_id BIGINT,

#     occurred_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

#     CONSTRAINT fk_usage_event_organization
#         FOREIGN KEY (organization_id)
#         REFERENCES organizations(organization_id)
#         ON DELETE CASCADE,

#     CONSTRAINT fk_usage_event_user
#         FOREIGN KEY (user_id)
#         REFERENCES users(user_id)
#         ON DELETE SET NULL,

#     CONSTRAINT chk_usage_quantity
#         CHECK (quantity > 0)
# );


# -- ============================================================
# -- 30. USAGE COUNTERS
# -- ============================================================

# CREATE TABLE IF NOT EXISTS usage_counters (
#     counter_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

#     organization_id BIGINT NOT NULL,

#     metric_key TEXT NOT NULL,

#     period_start DATE NOT NULL,

#     period_end DATE NOT NULL,

#     used_quantity NUMERIC(12, 2) NOT NULL DEFAULT 0,

#     limit_quantity NUMERIC(12, 2),

#     updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

#     CONSTRAINT fk_usage_counter_organization
#         FOREIGN KEY (organization_id)
#         REFERENCES organizations(organization_id)
#         ON DELETE CASCADE,

#     CONSTRAINT uq_usage_counter_period
#         UNIQUE (
#             organization_id,
#             metric_key,
#             period_start,
#             period_end
#         ),

#     CONSTRAINT chk_usage_counter_used
#         CHECK (used_quantity >= 0),

#     CONSTRAINT chk_usage_counter_limit
#         CHECK (
#             limit_quantity IS NULL
#             OR limit_quantity >= 0
#         ),

#     CONSTRAINT chk_usage_counter_dates
#         CHECK (period_end >= period_start)
# );


# -- ============================================================
# -- 31. CREDITS LEDGER
# -- ============================================================

# CREATE TABLE IF NOT EXISTS credits_ledger (
#     ledger_entry_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

#     organization_id BIGINT NOT NULL,

#     user_id BIGINT,

#     subscription_id BIGINT,

#     entry_type TEXT NOT NULL,

#     quantity NUMERIC(12, 2) NOT NULL,

#     balance_after NUMERIC(12, 2) NOT NULL,

#     expires_at TIMESTAMPTZ,

#     created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

#     CONSTRAINT fk_credit_organization
#         FOREIGN KEY (organization_id)
#         REFERENCES organizations(organization_id)
#         ON DELETE CASCADE,

#     CONSTRAINT fk_credit_user
#         FOREIGN KEY (user_id)
#         REFERENCES users(user_id)
#         ON DELETE SET NULL,

#     CONSTRAINT fk_credit_subscription
#         FOREIGN KEY (subscription_id)
#         REFERENCES subscriptions(subscription_id)
#         ON DELETE SET NULL
# );


# -- ============================================================
# -- INDEXES
# -- ============================================================


# -- Users / Auth

# CREATE INDEX IF NOT EXISTS idx_auth_sessions_user
#     ON auth_sessions(user_id);

# CREATE INDEX IF NOT EXISTS idx_auth_sessions_expires
#     ON auth_sessions(expires_at);


# -- Organizations

# CREATE INDEX IF NOT EXISTS idx_organizations_created_by
#     ON organizations(created_by_user_id);

# CREATE INDEX IF NOT EXISTS idx_org_members_user
#     ON organization_members(user_id);

# CREATE INDEX IF NOT EXISTS idx_org_members_organization
#     ON organization_members(organization_id);

# CREATE INDEX IF NOT EXISTS idx_org_members_status
#     ON organization_members(status);


# -- Resume system

# CREATE INDEX IF NOT EXISTS idx_resumes_user
#     ON resumes(user_id);

# CREATE INDEX IF NOT EXISTS idx_resumes_organization
#     ON resumes(organization_id);

# CREATE INDEX IF NOT EXISTS idx_candidate_profiles_user
#     ON candidate_profiles(user_id);

# CREATE INDEX IF NOT EXISTS idx_candidate_profiles_resume
#     ON candidate_profiles(source_resume_id);

# CREATE INDEX IF NOT EXISTS idx_job_descriptions_user
#     ON job_descriptions(user_id);

# CREATE INDEX IF NOT EXISTS idx_job_descriptions_organization
#     ON job_descriptions(organization_id);

# CREATE INDEX IF NOT EXISTS idx_job_descriptions_archived
#     ON job_descriptions(is_archived);


# -- Analysis / workflow

# CREATE INDEX IF NOT EXISTS idx_analysis_runs_user
#     ON analysis_runs(user_id);

# CREATE INDEX IF NOT EXISTS idx_analysis_runs_organization
#     ON analysis_runs(organization_id);

# CREATE INDEX IF NOT EXISTS idx_analysis_runs_resume
#     ON analysis_runs(resume_id);

# CREATE INDEX IF NOT EXISTS idx_analysis_runs_job
#     ON analysis_runs(job_description_id);

# CREATE INDEX IF NOT EXISTS idx_analysis_runs_status
#     ON analysis_runs(status);

# CREATE INDEX IF NOT EXISTS idx_workflow_steps_run
#     ON workflow_steps(run_id);

# CREATE INDEX IF NOT EXISTS idx_llm_requests_run
#     ON llm_requests(run_id);

# CREATE INDEX IF NOT EXISTS idx_llm_requests_step
#     ON llm_requests(step_id);

# CREATE INDEX IF NOT EXISTS idx_llm_requests_prompt
#     ON llm_requests(prompt_version_id);


# -- Generated resumes / analysis

# CREATE INDEX IF NOT EXISTS idx_generated_resumes_resume
#     ON generated_resumes(resume_id);

# CREATE INDEX IF NOT EXISTS idx_generated_resumes_template
#     ON generated_resumes(template_id);

# CREATE INDEX IF NOT EXISTS idx_generated_resumes_model
#     ON generated_resumes(model_id);

# CREATE INDEX IF NOT EXISTS idx_generated_resumes_profile
#     ON generated_resumes(profile_id);

# CREATE INDEX IF NOT EXISTS idx_generated_resumes_prompt
#     ON generated_resumes(prompt_version_id);

# CREATE INDEX IF NOT EXISTS idx_resume_analysis_resume
#     ON resume_analysis(resume_id);

# CREATE INDEX IF NOT EXISTS idx_resume_analysis_run
#     ON resume_analysis(run_id);

# CREATE INDEX IF NOT EXISTS idx_resume_analysis_model
#     ON resume_analysis(model_id);

# CREATE INDEX IF NOT EXISTS idx_analysis_scores_analysis
#     ON resume_analysis_scores(analysis_id);

# CREATE INDEX IF NOT EXISTS idx_feedback_analysis
#     ON analysis_feedback_items(analysis_id);

# CREATE INDEX IF NOT EXISTS idx_resume_version_resume
#     ON resume_version(resume_id);

# CREATE INDEX IF NOT EXISTS idx_resume_version_generated
#     ON resume_version(new_resume_id);


# -- Billing

# CREATE INDEX IF NOT EXISTS idx_plan_prices_plan
#     ON plan_prices(plan_id);

# CREATE INDEX IF NOT EXISTS idx_plan_entitlements_plan
#     ON plan_entitlements(plan_id);

# CREATE INDEX IF NOT EXISTS idx_billing_customers_organization
#     ON billing_customers(organization_id);

# CREATE INDEX IF NOT EXISTS idx_subscriptions_organization
#     ON subscriptions(organization_id);

# CREATE INDEX IF NOT EXISTS idx_subscriptions_plan
#     ON subscriptions(plan_id);

# CREATE INDEX IF NOT EXISTS idx_subscriptions_price
#     ON subscriptions(price_id);

# CREATE INDEX IF NOT EXISTS idx_subscriptions_status
#     ON subscriptions(status);

# CREATE INDEX IF NOT EXISTS idx_payment_orders_organization
#     ON payment_orders(organization_id);

# CREATE INDEX IF NOT EXISTS idx_payment_orders_subscription
#     ON payment_orders(subscription_id);

# CREATE INDEX IF NOT EXISTS idx_payment_orders_status
#     ON payment_orders(status);

# CREATE INDEX IF NOT EXISTS idx_payments_organization
#     ON payments(organization_id);

# CREATE INDEX IF NOT EXISTS idx_payments_order
#     ON payments(order_id);

# CREATE INDEX IF NOT EXISTS idx_payments_subscription
#     ON payments(subscription_id);

# CREATE INDEX IF NOT EXISTS idx_payments_status
#     ON payments(status);

# CREATE INDEX IF NOT EXISTS idx_invoices_organization
#     ON invoices(organization_id);

# CREATE INDEX IF NOT EXISTS idx_invoices_subscription
#     ON invoices(subscription_id);

# CREATE INDEX IF NOT EXISTS idx_invoices_payment
#     ON invoices(payment_id);

# CREATE INDEX IF NOT EXISTS idx_refunds_payment
#     ON refunds(payment_id);

# CREATE INDEX IF NOT EXISTS idx_webhook_events_status
#     ON payment_webhook_events(processing_status);

# CREATE INDEX IF NOT EXISTS idx_webhook_events_created
#     ON payment_webhook_events(created_at);


# -- Usage

# CREATE INDEX IF NOT EXISTS idx_usage_events_organization
#     ON usage_events(organization_id);

# CREATE INDEX IF NOT EXISTS idx_usage_events_user
#     ON usage_events(user_id);

# CREATE INDEX IF NOT EXISTS idx_usage_events_metric
#     ON usage_events(metric_key);

# CREATE INDEX IF NOT EXISTS idx_usage_events_occurred
#     ON usage_events(occurred_at);

# CREATE INDEX IF NOT EXISTS idx_usage_counters_organization
#     ON usage_counters(organization_id);

# CREATE INDEX IF NOT EXISTS idx_usage_counters_metric
#     ON usage_counters(metric_key);

# CREATE INDEX IF NOT EXISTS idx_credits_organization
#     ON credits_ledger(organization_id);

# CREATE INDEX IF NOT EXISTS idx_credits_user
#     ON credits_ledger(user_id);

# CREATE INDEX IF NOT EXISTS idx_credits_subscription
#     ON credits_ledger(subscription_id);

# CREATE INDEX IF NOT EXISTS idx_credits_created
#     ON credits_ledger(created_at);


# -- ============================================================
# -- PARTIAL INDEXES
# -- ============================================================

# -- Quickly find active sessions
# CREATE INDEX IF NOT EXISTS idx_auth_sessions_active
#     ON auth_sessions(user_id, expires_at)
#     WHERE revoked_at IS NULL;


# -- Quickly find active subscriptions
# CREATE INDEX IF NOT EXISTS idx_subscriptions_active
#     ON subscriptions(organization_id)
#     WHERE status IN ('active', 'trialing', 'past_due');


# -- Quickly find active plans
# CREATE INDEX IF NOT EXISTS idx_plans_active
#     ON plans(plan_key)
#     WHERE is_active = TRUE;


# -- Quickly find active prices
# CREATE INDEX IF NOT EXISTS idx_plan_prices_active
#     ON plan_prices(plan_id)
#     WHERE is_active = TRUE;


# -- Quickly find active entitlements
# CREATE INDEX IF NOT EXISTS idx_plan_entitlements_active
#     ON plan_entitlements(plan_id, entitlement_key)
#     WHERE is_active = TRUE;


# -- ============================================================
# -- OPTIONAL UPDATED_AT TRIGGER
# -- ============================================================

# CREATE OR REPLACE FUNCTION set_updated_at()
# RETURNS TRIGGER
# LANGUAGE plpgsql
# AS $$
# BEGIN
#     NEW.updated_at = CURRENT_TIMESTAMP;
#     RETURN NEW;
# END;
# $$;


# DROP TRIGGER IF EXISTS trg_users_updated_at
# ON users;

# CREATE TRIGGER trg_users_updated_at
# BEFORE UPDATE ON users
# FOR EACH ROW
# EXECUTE FUNCTION set_updated_at();


# DROP TRIGGER IF EXISTS trg_resume_templates_updated_at
# ON resume_templates;

# CREATE TRIGGER trg_resume_templates_updated_at
# BEFORE UPDATE ON resume_templates
# FOR EACH ROW
# EXECUTE FUNCTION set_updated_at();


# DROP TRIGGER IF EXISTS trg_job_descriptions_updated_at
# ON job_descriptions;

# CREATE TRIGGER trg_job_descriptions_updated_at
# BEFORE UPDATE ON job_descriptions
# FOR EACH ROW
# EXECUTE FUNCTION set_updated_at();


# DROP TRIGGER IF EXISTS trg_usage_counters_updated_at
# ON usage_counters;

# CREATE TRIGGER trg_usage_counters_updated_at
# BEFORE UPDATE ON usage_counters
# FOR EACH ROW
# EXECUTE FUNCTION set_updated_at();


# -- ============================================================
# -- END OF SCHEMA
# -- ============================================================