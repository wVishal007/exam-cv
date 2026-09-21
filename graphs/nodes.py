from agents.analyzer_agent import analyzer_model
from agents.resume_rewrite_agent import rewrite_model
from .agent_states import agentState
from data.format import assemble
class ResumeAgent:
    def __init__(self,analyzer_model,rewrite_model):
        self.analyzer_model = analyzer_model
        self.rewrite_model = rewrite_model

    def analyze_resume(self,data,guidelines):
        prompt = f"""
        You are a professional resume analyzer.

        Follow these guidelines:
        {guidelines}

        Analyze this resume:
        {data}
        """
        output = self.analyzer_model.invoke(prompt)
        return output
    # def rewrite_resume(self,data,feedback,format,guidelines):
    #     prompt = f"""
    #     You are a professional resume writer.

    #     Rewrite the resume according to the provided guidelines
    #     and feedback also keep resume strictly one page long amd strictly follow the given format.

    #     Resume:
    #     {data}

    #     Analyzer Feedback:
    #     {feedback}

    #     Required Format:
    #     {format}

    #     Guidelines:
    #     {guidelines}
    #     """
    #     output = self.rewrite_model.invoke(prompt)
    #     return output

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
    response = agent.analyze_resume(
        state['data'],state['guidelines']
    )

    # state['ats_score']=response.ats_score
    # state['feedback']=response.feedback
    # state['suggestions']=response.suggestions
    return {
        "ats_score": response.ats_score,
        "feedback": response.feedback,
        "suggestions": response.suggestions,
    }

    
# def rewrite(state:agentState):
#     response = agent.rewrite_resume(
#         state['data'],state['feedback'],state['format'],state['guidelines']
#     )
#     max_ats_score = max(state['ats_score'],response.ats_score)

#     # latex = response.latex_code

#     # if not latex.startswith("\\documentclass"):
#     #     raise ValueError("Generated resume does not start with \\documentclass")

#     # if "\\begin{document}" not in latex:
#     #     raise ValueError("Generated resume is missing \\begin{document}")

#     # if not latex.endswith("\\end{document}"):
#     #     raise ValueError("Generated resume is missing \\end{document}")

#     max_ats_score = max(state["ats_score"], response.ats_score)
    
#     # state['rewritten_resume']=response.latex_code
#     # state['feedback']=response.feedback,   
#     # state['suggestions']=response.suggestions   
#     return {
#         "ats_score": max_ats_score,
#         "rewritten_resume": response.latex_code,
#         # "feedback": response.feedback,
#         # "suggestions": response.suggestions,
#     }

def rewrite(state: agentState):
    response = agent.rewrite_resume(
        data=state["data"],
        feedback=state["feedback"],
        format=state["format"],
        format_rules=state["format_rules"],
        guidelines=state["guidelines"],
    )

    final_latex = assemble(response.latex_code)

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