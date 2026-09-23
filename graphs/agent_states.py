from pydantic import BaseModel,Field
from typing import TypedDict,Annotated

class agentState(TypedDict):
    data : str
    guidelines : str
    format : str
    format_rules : str
    job_description : str
    job_vs_resume_analysis : dict
    # profile: dict

    ats_score : int
    max_ats_score : int
    rewritten_resume : str
    feedback : str
    suggestions : str
