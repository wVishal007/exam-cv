from dotenv import load_dotenv
load_dotenv()

from data.guidelines import guidelines
from data.format import format,format_rules
from utils.pdf_read import extract_resume_text,select_resume_pdf

from graphs.workflow import workflow

def main():
    print("="*30)
    print("AI RESUME ANALYZER")
    print("select your resume")
    pdf_path = select_resume_pdf()
    print("getting resume-data")
    data = extract_resume_text(pdf_path)
    output = workflow.invoke({
    "data":data,
    "guidelines" : guidelines,
    "format" : format,
    "format_rules":format_rules
    })
    print("="*30)
    print(output["ats_score"])
    print("-"*30)
    print(output["suggestions"])
    print("-"*30)
    print(output["feedback"])
    print("-"*30)
    if output.get("rewritten_resume"):
        print(output["rewritten_resume"])
    else:
        print("=" * 30)
        print("analyzation done")

if __name__ == "__main__":
    main()
