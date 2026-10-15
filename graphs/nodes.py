from agents.analyzer_agent import analyzer_model
from agents.resume_rewrite_agent import rewrite_model
from .agent_states import agentState
from utils.mapping import template_map,assemble_map,format_rules_map
from utils.candidate_info import extract_candidate_info
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

def analyze(state: agentState):
    response = agent.analyze_resume(
        state["data"],
        state["guidelines"],
        state["job_description"]
    )

    return {
        "ats_score": response.ats_score,
        "feedback": response.feedback,
        "suggestions": response.suggestions,
        "job_vs_resume_analysis": response.job_vs_resume_analysis.job_analysis_feed_back,
        "analysis_match_score": response.job_vs_resume_analysis.analysis_match_score
    }


def rewrite(state: agentState):
    selected_format = state["resume_format"]
    response = agent.rewrite_resume(
        data=state["data"],
        feedback=state["feedback"],
        format=template_map[selected_format],
        format_rules=format_rules_map[selected_format],
        guidelines=state["guidelines"],
    )
    # Identity comes from the uploaded resume, not from the template, so the
    # same template renders a different header for every candidate.
    info = extract_candidate_info(state["data"])
    final_latex = assemble_map[selected_format](response.latex_code, info=info)

    max_ats_score = max(
        state["ats_score"],
        response.ats_score
    )

    return {
        "ats_score": max_ats_score,
        "latex_code": final_latex,
    }
    
def conditional_node(state:agentState):
    query = state["scope"]
    if query == 1:
        return "end"
    else:
        return "rewrite"