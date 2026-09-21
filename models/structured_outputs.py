from pydantic import BaseModel,Field
from typing import TypedDict,Annotated

class analyzer_output(BaseModel):
    ats_score : int = Field(description="ats score of the resume calculated as per guidelines",ge=1,le=100)
    feedback : str = Field(description="feedback of the candidate's resume")
    suggestions : str = Field(description="suggestion for candidate for his future goals and plans")
class rewrite_output(BaseModel):
    ats_score : int = Field(description="ats score of the new rewritten resume calculated as per guidelines",ge=1,le=100)
    latex_code : str = Field(description="latex code generated for candidates resume using the given format")
    
