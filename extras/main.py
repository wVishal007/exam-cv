import sys
from pathlib import Path

# Moved to extras/. Put the project root on sys.path so the absolute imports
# below (data.*, utils.*, graphs.*) keep working.
_PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from data.guidelines import guidelines
from utils.pdf_read import extract_resume_text,select_resume_pdf
from utils.latex_compiler import generate_pdf_from_latex
from graphs.resume_workflow import workflow


def main():
    print("="*30)
    print("AI RESUME ANALYZER")
    print("select your resume")
    pdf_path = select_resume_pdf()
    print("getting resume-data")
    data = extract_resume_text(pdf_path)
    output = workflow.invoke({
    "data":data["resume_data"],
    "guidelines" : guidelines,
    })
    print("="*30)
    print(output["ats_score"])
    print("-"*30)
    print(output["suggestions"])
    print("-"*30)
    print(output["feedback"])
    print("-"*30)
    print(output["job_vs_resume_analysis"])
    print("-"*30)
    if output.get("rewritten_resume"):
        # print("="*15," [latext_code] ","="*20)
        # print(output["rewritten_resume"])

        final_pdf = generate_pdf_from_latex(output["rewritten_resume"],data["file_name"])
        print(f"PDF generated: {final_pdf}")
        print("-" * 30)
        print("resume rewrite done")

    else:
        print("=" * 30)
        print("analyzation done")

if __name__ == "__main__":
    main()
