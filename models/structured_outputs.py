from pydantic import BaseModel,Field

class job_vs_resume_analysis_class(BaseModel):
    analysis_match_score:int = Field(description="ats score of the new rewritten resume calculated as per guidelines if job description not provided answer 0",ge=1,le=100)
    job_analysis_feed_back : str = Field(description="feedback of the candidate's resume vs job description if job description not provided just answer no job description provided")

class analyzer_output(BaseModel):
    ats_score : int = Field(description="ats score of the resume calculated as per guidelines",ge=1,le=100)
    feedback : str = Field(description="feedback of the candidate's resume")
    suggestions : str = Field(description="suggestion for candidate for his future goals and plans")
    job_vs_resume_analysis :job_vs_resume_analysis_class
class rewrite_output(BaseModel):
    ats_score : int = Field(description="ats score of the new rewritten resume calculated as per guidelines",ge=1,le=100)
    latex_code : str = Field(description="latex code generated for candidates resume using the given format")
    


