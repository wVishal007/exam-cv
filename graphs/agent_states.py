from typing import TypedDict

class agentState(TypedDict):
    data : str
    guidelines : str
    format : str
    format_rules : str
    job_description : str
    job_vs_resume_analysis : dict
    analysis_match_score: int

    scope:int
    resume_format : int

    # profile: dict
    ats_score : int
    max_ats_score : int
    latex_code : str
    feedback : str
    suggestions : str
