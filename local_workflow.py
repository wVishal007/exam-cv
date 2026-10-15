"""
local_workflow.py
=================

Single-file LangGraph workflow with a dark-mode Tkinter GUI for the
resume analyzer.

The graph part REUSES the real building blocks (identical to production):

    * agentState              - the production state schema   (graphs.agent_states)
    * ResumeAgent instance    - real prompts + LLM calls      (graphs.nodes: `agent`)
    * template maps           - real template/assemble/rules  (utils.mapping)

The node functions below are THIN, editable wrappers around the shared `agent`
and template maps. They intentionally mirror graphs/nodes.py so behaviour stays
consistent, but you can tweak them here to prototype changes safely.

The GUI mirrors the original pre-FastAPI CLI flow:

    Select PDF (filedialog)
      -> paste a job description (optional)
      -> choose mode: analyze only (scope=1) or analyze + rewrite (scope=2)
      -> pick a template (1-11) for rewrite
      -> progress window while the real workflow runs in a background thread
      -> results: ATS score, feedback, suggestions, JD match
         and (for rewrite) LaTeX with "Save as .tex" / "Save as PDF"

Production is untouched: FastAPI -> api/controllers -> graphs.workflow.

Usage
-----
    python local_workflow.py             # launch the GUI
    python local_workflow.py --dry-run   # print graph structure, no LLM / GUI
"""

# --------------------------------------------------------------------------- #
# 1. STATE
# --------------------------------------------------------------------------- # 

# --------------------------------------------------------------------------- #
# 2. AGENT LOGIC (reused, not duplicated)
# --------------------------------------------------------------------------- #
from graphs.nodes import agent                     # ResumeAgent(analyzer, rewrite)
from utils.mapping import template_map, assemble_map, format_rules_map
from utils.candidate_info import extract_candidate_info
from data.guidelines import guidelines
from langgraph.graph import StateGraph, START, END
from langgraph.graph.state import CompiledStateGraph

import shutil
import subprocess
import tempfile
from pathlib import Path

import threading
import tkinter as tk
from tkinter import filedialog, messagebox

import ttkbootstrap as ttk
from utils.pdf_read import extract_resume_text
import argparse
from graphs.agent_states import agentState

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
    final_latex = assemble_map[selected_format](
        response.latex_code, info=extract_candidate_info(state["data"])
    )
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


def run_local(
    data: str,
    job_description: str = "",
    resume_format: int = 1,
    scope: int = 1,
    guidelines_text: str = guidelines,
) -> dict:
    """Programmatic entry point - invoke the local workflow directly."""
    return workflow.invoke(
        {
            "data": data,
            "guidelines": guidelines_text,
            "job_description": job_description,
            "scope": scope,
            "resume_format": resume_format,
        }
    )


# --------------------------------------------------------------------------- #
# 6. PDF COMPILATION (self-contained; GUI-safe, no terminal input())
# --------------------------------------------------------------------------- #



def _compile_pdf(latex_code: str, pdf_dest: str) -> str:
    """Compile LaTeX into the given PDF path via pdflatex. Returns a status msg."""
    pdf_dest = Path(pdf_dest)
    temp_dir = Path(tempfile.mkdtemp())
    stem = pdf_dest.stem
    try:
        tex_file = temp_dir / f"{stem}.tex"
        tex_file.write_text(latex_code, encoding="utf-8")

        result = subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", f"{stem}.tex"],
            cwd=temp_dir,
            capture_output=True,
            text=True,
            timeout=180,
        )
        pdf_file = temp_dir / f"{stem}.pdf"
        if not pdf_file.exists():
            tail = (result.stdout or "")[-2000:] + "\n" + (result.stderr or "")[-2000:]
            raise RuntimeError(f"pdflatex could not produce {stem}.pdf.\n\n{tail}")
        shutil.copy(str(pdf_file), str(pdf_dest))
    finally:
        shutil.rmtree(str(temp_dir), ignore_errors=True)
    return f"PDF saved to:\n{pdf_dest}"


# --------------------------------------------------------------------------- #
# 7. DARK-MODE GUI
# --------------------------------------------------------------------------- #

BG = "#1a1a2e"
PANEL = "#222244"
ACCENT = "#e94560"


class ResumeAnalyzerApp:
    def __init__(self) -> None:
        self.root = ttk.Window(themename="darkly", title="AI Resume Analyzer")
        self.root.geometry("1000x760")
        self.root.minsize(860, 640)

        self.resume_text = ""
        self.resume_name = ""
        self.latex_code = ""

        self.container = ttk.Frame(self.root, padding=20)
        self.container.pack(fill="both", expand=True)
        self.container.configure(style="TFrame")

        self._show_setup()

    # ---------------------------------------------------------------- views
    def _clear(self) -> None:
        for child in self.container.winfo_children():
            child.destroy()

    def _show_setup(self) -> None:
        self._clear()
        setup = ttk.Frame(self.container)
        setup.pack(fill="both", expand=True)

        title = ttk.Label(
            setup, text="AI RESUME ANALYZER", font=("Segoe UI", 22, "bold")
        )
        title.pack(pady=(0, 4))
        ttk.Label(
            setup, text="Full pipeline: analysis, JD matching, optional LaTeX rewrite",
            font=("Segoe UI", 10),
        ).pack(pady=(0, 18))

        # --- Resume file ---
        file_card = ttk.Frame(setup, padding=12, bootstyle="secondary")
        file_card.pack(fill="x", pady=6)
        self.file_label = ttk.Label(file_card, text="No resume selected", font=("Segoe UI", 11))
        self.file_label.pack(side="left", fill="x", expand=True)
        ttk.Button(file_card, text="Select PDF", command=self._pick_pdf,
                   bootstyle="primary").pack(side="right")

        # --- Job description ---
        jd_frame = ttk.Frame(setup, padding=12, bootstyle="secondary")
        jd_frame.pack(fill="both", expand=True, pady=6)
        ttk.Label(jd_frame, text="Job Description (optional, paste here)",
                  font=("Segoe UI", 10, "bold")).pack(anchor="w")
        self.jd_text = ttk.ScrolledText(jd_frame, height=5, wrap="word")
        self.jd_text.pack(fill="both", expand=True, pady=(6, 0))

        # --- Mode + template ---
        opts = ttk.Frame(setup)
        opts.pack(fill="x", pady=10)

        mode_frame = ttk.Frame(opts, padding=12, bootstyle="secondary")
        mode_frame.pack(side="left", fill="both", expand=True)
        ttk.Label(mode_frame, text="Mode", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        self.mode_var = tk.IntVar(value=1)
        ttk.Radiobutton(mode_frame, text="Analyze only (ATS + JD match)",
                        variable=self.mode_var, value=1,
                        command=self._toggle_template).pack(anchor="w", pady=2)
        ttk.Radiobutton(mode_frame, text="Analyze + rewrite as LaTeX",
                        variable=self.mode_var, value=2,
                        command=self._toggle_template).pack(anchor="w", pady=2)

        tpl_frame = ttk.Frame(opts, padding=12, bootstyle="secondary")
        tpl_frame.pack(side="left", fill="both", expand=True, padx=10)
        ttk.Label(tpl_frame, text="Template (for rewrite)", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        self.tpl_combo = ttk.Combobox(
            tpl_frame, values=[str(i) for i in range(1, 12)], state="readonly", width=6
        )
        self.tpl_combo.set("1")
        self.tpl_combo.pack(anchor="w", pady=4)
        self.tpl_hint = ttk.Label(tpl_frame, text="semantics of template_map[1]",
                                  font=("Segoe UI", 9), wraplength=380, justify="left")
        self.tpl_hint.pack(anchor="w")
        self.tpl_combo.bind("<<ComboboxSelected>>", self._update_tpl_hint)
        self.tpl_hint.configure(text="Template 1 - classic ATS-safe layout")
        self._toggle_template()

        ttk.Button(setup, text="Run Analysis", command=self._run,
                   bootstyle="success", width=20).pack(pady=14)

    def _show_progress(self) -> None:
        self._clear()
        prog = ttk.Frame(self.container)
        prog.pack(fill="both", expand=True)
        ttk.Label(prog, text="Working...", font=("Segoe UI", 16, "bold")).pack(pady=(80, 8))
        status = ttk.Label(prog, text="Analyzing resume with the LLM. This can take a minute.",
                           font=("Segoe UI", 10))
        status.pack(pady=(0, 20))
        gauge = ttk.Progressbar(prog, mode="indeterminate", length=420, bootstyle="primary")
        gauge.pack()
        gauge.start(12)
        self._progress_widgets = (status, gauge)

    def _show_results(self, result: dict) -> None:
        self._clear()
        res = ttk.Frame(self.container)
        res.pack(fill="both", expand=True)

        ats = result.get("ats_score") or 0
        match = result.get("analysis_match_score") or 0

        header = ttk.Frame(res)
        header.pack(fill="x", pady=(0, 10))
        color = "success" if ats >= 80 else ("warning" if ats >= 50 else "danger")
        ttk.Meter(
            header, amount_total=100, amount_used=ats,
            meter_size=150, meter_thickness=12,
            subtext=f"ATS {ats}/100", bootstyle=color,
        ).pack(side="left")

        if result.get("analysis_match_score") is not None:
            mcolor = "success" if match >= 80 else ("warning" if match >= 50 else "danger")
            ttk.Meter(
                header, amount_total=100, amount_used=match,
                meter_size=150, meter_thickness=12,
                subtext=f"Match {match}/100", bootstyle=mcolor,
            ).pack(side="left", padx=20)

        header_label = ttk.Label(
            header, text="Analysis complete",
            font=("Segoe UI", 16, "bold"), bootstyle="success"
        )
        header_label.pack(side="left", padx=20)

        ttk.Label(res, text=f"Resume: {self.resume_name}", font=("Segoe UI", 10)).pack(anchor="w")

        notebook = ttk.Notebook(res)
        notebook.pack(fill="both", expand=True, pady=(6, 0))

        # --- Analysis tab ---
        analysis_tab = ttk.Frame(notebook, padding=8)
        notebook.add(analysis_tab, text="  Analysis  ")

        text = ttk.ScrolledText(analysis_tab, wrap="word", font=("Consolas", 10))
        text.pack(fill="both", expand=True)
        _dump = f"""FEEDBACK
{result.get("feedback", "")}

SUGGESTIONS
{result.get("suggestions", "")}

JOB VS RESUME
{result.get("job_vs_resume_analysis", "No job description provided")}
"""
        text.insert("1.0", _dump)
        text.configure(state="disabled")

        # --- LaTeX tab ---
        if result.get("latex_code"):
            self.latex_code = result["latex_code"]
            latex_tab = ttk.Frame(notebook, padding=8)
            notebook.add(latex_tab, text="  LaTeX  ")

            code = ttk.ScrolledText(latex_tab, wrap="none", font=("Consolas", 10))
            code.pack(fill="both", expand=True)
            code.insert("1.0", self.latex_code)
            code.configure(state="disabled")

            btns = ttk.Frame(latex_tab)
            btns.pack(fill="x", pady=(8, 0))
            ttk.Button(btns, text="Save as .tex", command=self._save_tex,
                       bootstyle="primary").pack(side="left")
            ttk.Button(btns, text="Save as PDF", command=self._save_pdf,
                       bootstyle="success").pack(side="left", padx=6)
            ttk.Button(btns, text="Copy LaTeX", command=self._copy_latex,
                       bootstyle="info").pack(side="left")

        bottom = ttk.Frame(res)
        bottom.pack(fill="x", pady=(10, 0))
        ttk.Button(bottom, text="New Analysis", command=self._show_setup,
                   bootstyle="secondary").pack(side="right")

    def _show_error(self, exc: Exception) -> None:
        self._clear()
        err = ttk.Frame(self.container)
        err.pack(fill="both", expand=True)
        ttk.Label(err, text="Something went wrong", font=("Segoe UI", 16, "bold"),
                  bootstyle="danger").pack(pady=(60, 8))
        msg = ttk.ScrolledText(err, wrap="word", height=12, font=("Consolas", 10))
        msg.pack(fill="both", expand=True, padx=10)
        msg.insert("1.0", str(exc) or repr(exc))
        msg.configure(state="disabled")
        ttk.Button(err, text="Back", command=self._show_setup,
                   bootstyle="secondary", width=16).pack(pady=12)

    # ---------------------------------------------------------------- helpers
    def _toggle_template(self) -> None:
        rewrite = self.mode_var.get() == 2
        state = "readonly" if rewrite else "disabled"
        self.tpl_combo.configure(state=state)

    def _update_tpl_hint(self, _event=None) -> None:
        n = int(self.tpl_combo.get())
        self.tpl_hint.configure(text=f"Template {n} selected")
        # first 120 chars of the template actually loaded (real description)
        snippet = (template_map[n] or "").strip().splitlines()
        first = next((l.strip() for l in snippet if l.strip() and not l.strip().startswith("%")
                      and not l.strip().startswith("\\")), snippet[0].strip() if snippet else "")
        self.tpl_hint.configure(text=f"Template {n}: {first[:80]}")

    def _pick_pdf(self) -> None:
        path = filedialog.askopenfilename(
            title="Select your resume",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
        )
        if not path:
            return
        

        extracted = extract_resume_text(path)
        self.resume_text = extracted["resume_data"]
        self.resume_name = extracted["file_name"]
        self.file_label.configure(text=f"Loaded: {self.resume_name}")

    def _run(self) -> None:
        if not self.resume_text:
            messagebox.showwarning("No resume", "Select a resume PDF first.", parent=self.root)
            return
        jd = self.jd_text.get("1.0", tk.END).strip()
        scope = self.mode_var.get()
        try:
            resume_format = int(self.tpl_combo.get()) if scope == 2 else 1
        except (TypeError, ValueError):
            resume_format = 1

        state = {
            "data": self.resume_text,
            "guidelines": guidelines,
            "job_description": jd,
            "scope": scope,
            "resume_format": resume_format,
        }
        self._show_progress()
        threading.Thread(target=self._worker, args=(state,), daemon=True).start()

    def _worker(self, state: dict) -> None:
        try:
            result = workflow.invoke(state)
            self.root.after(0, lambda: self._show_results(result))
        except Exception as exc:  # surface any LLM/network/graph error to the GUI
            self.root.after(0, lambda: self._show_error(exc))

    # ---------------------------------------------------------------- saves
    def _save_tex(self) -> None:
        if not self.latex_code:
            return
        default = f"{self.resume_name or 'resume'}_rewritten.tex"
        path = filedialog.asksaveasfilename(
            title="Save LaTeX", initialfile=default,
            defaultextension=".tex",
            filetypes=[("LaTeX source", "*.tex"), ("All files", "*.*")],
        )
        if not path:
            return
        Path(path).write_text(self.latex_code, encoding="utf-8")
        messagebox.showinfo("Saved", f"LaTeX saved to:\n{path}", parent=self.root)

    def _save_pdf(self) -> None:
        if not self.latex_code:
            return
        default = f"{self.resume_name or 'resume'}_rewritten.pdf"
        path = filedialog.asksaveasfilename(
            title="Save PDF", initialfile=default,
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
        )
        if not path:
            return
        try:
            msg = _compile_pdf(self.latex_code, path)
        except Exception as exc:
            messagebox.showerror("PDF compilation failed", str(exc), parent=self.root)
            return
        messagebox.showinfo("Saved", msg, parent=self.root)

    def _copy_latex(self) -> None:
        if self.latex_code:
            self.root.clipboard_clear()
            self.root.clipboard_append(self.latex_code)
            messagebox.showinfo("Copied", "LaTeX copied to clipboard.", parent=self.root)


def main() -> None:

    parser = argparse.ArgumentParser(description="Local resume workflow (GUI)")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print compiled graph structure + state fields, then exit (no GUI, no LLM)",
    )
    args = parser.parse_args()

    if args.dry_run:
        print("=== Compiled local workflow ===")
        print(workflow.get_graph().draw_mermaid())
        print("\n=== State fields ===")
        print("\n".join(f"  - {k}" for k in agentState.__annotations__))
        raise SystemExit(0)

    ResumeAnalyzerApp().root.mainloop()


if __name__ == "__main__":
    main()