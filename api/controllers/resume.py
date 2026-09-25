from data.guidelines import guidelines
# from utils.pdf_read import extract_resume_text,select_resume_pdf
# from utils.latex_compiler import generate_pdf_from_latex
from graphs.workflow import workflow

def analyze_resume(data:str,job_description:str):
    try:
        response = workflow.invoke({
            "data":data,
            "guidelines":guidelines,
            "job_description":job_description,
            "scope":1
        })

        return {
            "ats_score":response["ats_score"],
            "feedback":response["feedback"],
            "job_vs_resume_analysis":response["job_vs_resume_analysis"],
            "suggestions":response["suggestions"],
            "analysis_match_score":response["analysis_match_score"]
        }
    except Exception:
        return {
            "message":"resume analysis failed",
            "success":False
        }
    # except Exception as e:
    #     print("RESUME ANALYSIS ERROR:", repr(e))
    #     raise

def rewrite_resume(data:str,job_description:str,resume_format:int):
    try:
        response = workflow.invoke({
            "data":data,
            "guidelines":guidelines,
            "job_description":job_description,
            "scope":2,
            "resume_format":resume_format
        })
        return {
            "ats_score":response["ats_score"],
            "feedback":response["feedback"],
            "job_vs_resume_analysis":response["job_vs_resume_analysis"],
            "suggestions":response["suggestions"],
            "analysis_match_score":response["analysis_match_score"],
            "latex_code":response["latex_code"]
        }
    # except Exception:
    #     return {
    #         "message":"resume analysis failed",
    #         "success":False
    #     }
    except Exception as e:
        print("RESUME ANALYSIS ERROR:", e)
        raise

