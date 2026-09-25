"""
local_workflow.py
=================

Single-file LangGraph workflow for LOCAL experimentation / testing.

Purpose
-------
The production pipeline is split across graphs/agent_states.py, graphs/nodes.py,
graphs/workflow.py. For quick experiments with the resume analyzer (new nodes,
new routing, new state fields) you can work in this one file instead of hunting
through the whole production architecture.

This file REUSES the real building blocks:

    * agentState              - the production state schema  (graphs.agent_states)
    * ResumeAgent instance    - real prompts + LLM calls     (graphs.nodes: `agent`)
    * template maps           - real template/assemble/rules (utils.mapping)

The node functions below are THIN, editable wrappers around the shared `agent`
and template maps. They intentionally mirror graphs/nodes.py so behaviour stays
consistent, but you can tweak them here to prototype changes safely.

Production is untouched: FastAPI -> api/controllers -> graphs.workflow.

CHAIN (in one file)
-------------------
    State (agentState)
      -> analyze node
      -> conditional node (scope == 1 ? end : rewrite)
      -> rewrite node
      -> compiled workflow
      -> local invocation (__main__)
"""

# --------------------------------------------------------------------------- #
# 1. STATE
# --------------------------------------------------------------------------- #
from graphs.agent_states import agentState

# --------------------------------------------------------------------------- #
# 2. AGENT LOGIC (reused, not duplicated)
# --------------------------------------------------------------------------- #
from graphs.nodes import agent                     # ResumeAgent(analyzer, rewrite)
from utils.mapping import template_map, assemble_map, format_rules_map
from data.guidelines import guidelines
from langgraph.graph import StateGraph, START, END
from langgraph.graph.state import CompiledStateGraph

# --------------------------------------------------------------------------- #
# 3. NODES (editable experiment surface; mirror graphs/nodes.py)
# --------------------------------------------------------------------------- #


def analyze(state: agentState) -> dict:
    """Analyze the resume against guidelines + optional job description."""
    response = agent.analyze_resume(
        data=state["data"],
        guidelines=state["guidelines"],
        job_description=state["job_description"],
    )
    return {
        "ats_score": response.ats_score,
        "feedback": response.feedback,
        "suggestions": response.suggestions,
        "job_vs_resume_analysis": response.job_vs_resume_analysis.job_analysis_feed_back,
        "analysis_match_score": response.job_vs_resume_analysis.analysis_match_score,
    }


def rewrite(state: agentState) -> dict:
    """Rewrite the resume with the selected template and re-assemble the LaTeX."""
    selected_format = state["resume_format"]
    response = agent.rewrite_resume(
        data=state["data"],
        feedback=state["feedback"],
        format=template_map[selected_format],
        format_rules=format_rules_map[selected_format],
        guidelines=state["guidelines"],
    )
    final_latex = assemble_map[selected_format](response.latex_code)
    return {
        "ats_score": max(state["ats_score"], response.ats_score),
        "latex_code": final_latex,
    }


def conditional_node(state: agentState) -> str:
    """Route: scope == 1 -> stop; otherwise go to rewrite."""
    return "end" if state["scope"] == 1 else "rewrite"


# --------------------------------------------------------------------------- #
# 4. CONDITIONAL ROUTING MAP
# --------------------------------------------------------------------------- #
ROUTING_MAP = {
    "end": END,
    "rewrite": "rewrite",
}

# --------------------------------------------------------------------------- #
# 5. LANGGRAPH CONSTRUCTION + COMPILATION
# --------------------------------------------------------------------------- #
def build_workflow() -> CompiledStateGraph:
    """Build and compile the local StateGraph.

    To experiment: add/remove nodes, change edges, or tweak ROUTING_MAP above,
    then call build_workflow() again.
    """
    graph = StateGraph(agentState)
    graph.add_node("analyze", analyze)
    graph.add_node("rewrite", rewrite)
    graph.add_edge(START, "analyze")
    graph.add_conditional_edges("analyze", conditional_node, ROUTING_MAP)
    graph.add_edge("rewrite", END)
    return graph.compile()


workflow = build_workflow()


# --------------------------------------------------------------------------- #
# 6. LOCAL INVOCATION
# --------------------------------------------------------------------------- #
def run_local(
    data: str,
    job_description: str = "",
    resume_format: int = 1,
    scope: int = 1,
    guidelines_text: str = guidelines,
) -> dict:
    """Invoke the local workflow with the real LLM agents."""
    return workflow.invoke(
        {
            "data": data,
            "guidelines": guidelines_text,
            "job_description": job_description,
            "scope": scope,
            "resume_format": resume_format,
        }
    )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run the local resume workflow")
    parser.add_argument("pdf_path", nargs="?", help="Path to a resume PDF to analyze")
    parser.add_argument(
        "--rewrite",
        type=int,
        default=None,
        help="Also rewrite using template N (1-6); scope=2",
    )
    parser.add_argument("--jd", default="", help="Job description text")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print graph structure and state fields without calling the LLM",
    )
    args = parser.parse_args()

    if args.dry_run:
        print("=== Compiled local workflow ===")
        print(workflow.get_graph().draw_mermaid())
        print("\n=== State fields ===")
        print("\n".join(f"  - {k}" for k in agentState.__annotations__))
        raise SystemExit(0)

    if args.pdf_path:
        from utils.pdf_read import extract_resume_text

        sample_data = extract_resume_text(args.pdf_path)["resume_data"]
    else:
        sample_data = (
            "Vishal Singh\n"
            "Backend / AI Engineer\n"
            "Skills: Python, FastAPI, PostgreSQL, LangGraph, Gemini\n"
            "Experience: Built a resume analyzer using LangGraph and Gemini.\n"
            "Projects: resume-llm - ATS resume analysis and rewriting system.\n"
        )

    scope = 2 if args.rewrite else 1
    result = run_local(
        data=sample_data,
        job_description=args.jd,
        resume_format=args.rewrite if args.rewrite else 1,
        scope=scope,
    )

    print("=" * 40)
    print("ATS SCORE:", result["ats_score"])
    print("-" * 40)
    print("FEEDBACK:", result["feedback"])
    print("-" * 40)
    print("SUGGESTIONS:", result["suggestions"])
    print("-" * 40)
    print("JOB VS RESUME:", result["job_vs_resume_analysis"])
    print("-" * 40)
    print("MATCH SCORE:", result["analysis_match_score"])
    if result.get("latex_code"):
        print("-" * 40)
        print("LATEX LENGTH:", len(result["latex_code"]))