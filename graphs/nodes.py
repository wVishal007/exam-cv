from agents.analyzer_agent import analyzer_model
from agents.resume_rewrite_agent import rewrite_model
from .agent_states import agentState
from utils.mapping import template_map,assemble_map,format_rules_map
class ResumeAgent:
    def __init__(self,analyzer_model,rewrite_model):
        self.analyzer_model = analyzer_model
        self.rewrite_model = rewrite_model

    def analyze_resume(self,data,guidelines,job_description):
        prompt = f"""
        You are a professional resume analyzer.

        Follow these guidelines:
        {guidelines}

        Analyze this resume:
        {data}

        job description if available
        {job_description}

        """
        output = self.analyzer_model.invoke(prompt)
        return output

    def rewrite_resume(
        self,
        data,
        feedback,
        format,
        format_rules,
        guidelines,
    ):
        prompt = f"""
        You are a professional resume writer.

        Your task is to rewrite the candidate's resume.

        IMPORTANT:

        - Preserve factual accuracy.
        - Never invent information.
        - Improve ATS compatibility.
        - Improve clarity and technical impact.
        - Keep the resume strictly one page.
        - Follow the provided LaTeX format exactly.
        - The preamble, macros, and header are LOCKED.
        - Only the BODY may be rewritten.

        ORIGINAL RESUME:
        ----------------
        {data}

        ANALYZER FEEDBACK:
        ------------------
        {feedback}

        RESUME GUIDELINES:
        ------------------
        {guidelines}

        REQUIRED FORMAT:
        ----------------
        {format}

        LATEX FORMAT RULES:
        -------------------
        {format_rules}

        Return ONLY the LaTeX source.
        """

        output = self.rewrite_model.invoke(prompt)

        return output
agent = ResumeAgent(analyzer_model,rewrite_model)

def analyze(state:agentState):
    print("Enter job description.")
    print("Paste the complete job description.")
    print("When finished, type END on a new line.")
    
    job_description_lines = []
    
    while True:
        line = input()
    
        if line.strip() == "END":
            break
        
        job_description_lines.append(line)
    
    job_description = "\n".join(job_description_lines)
    if len(job_description) != 0:
        state["job_description"]=job_description
        response = agent.analyze_resume(
            state['data'],state['guidelines'],job_description
        )
    else:
        state[job_description]=""      
        response = agent.analyze_resume(
            state['data'],state['guidelines'],job_description=""
        )
    return {
            "ats_score": response.ats_score,
            "feedback": response.feedback,
            "suggestions": response.suggestions,
            "job_vs_resume_analysis":response.job_vs_resume_analysis
            }


def rewrite(state: agentState):
    selected_format = int(input("enter the format you want to use out of 1,2,3,4,5,6 : "))
    response = agent.rewrite_resume(
        data=state["data"],
        feedback=state["feedback"],
        format=template_map[selected_format],
        format_rules=format_rules_map[selected_format],
        guidelines=state["guidelines"],
    )
    final_latex = assemble_map[selected_format](response.latex_code)

    # final_latex = assemble(response.latex_code)

    max_ats_score = max(
        state["ats_score"],
        response.ats_score
    )

    return {
        "ats_score": max_ats_score,
        "rewritten_resume": final_latex,
    }
    
def conditional_node(state:agentState):
    query = input("enter your choice [1] analyze or rewrite [2] : ")
    if query == "1":
        return "end"
    else:
        return "rewrite"