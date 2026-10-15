from api.controllers.resume import analyze_resume,rewrite_resume
from api.routes.auth import get_current_user
from database.operations.upload_resume import upload_resume
from database.operations.generate_resume import save_generated_resume,get_rewrite_history,get_generated_resume_pdf
from utils.pdf_read import extract_resume_text
from database.operations.resume_analysis import create_analysis,get_analysis_history
from fastapi import APIRouter, UploadFile, Depends, File, Form
from database.operations.resume_templates import get_templates
from agents.analyzer_agent import analyzer_model_id
from agents.resume_rewrite_agent import rewrite_model_id
from utils.latex_compiler import generate_pdf_from_latex
from utils.cloudinary_upload import upload_resume_preview
from utils.pdf_preview import generate_pdf_preview
from fastapi.responses import Response
from pathlib import Path
from fastapi import HTTPException
import tempfile
import os

router = APIRouter()


@router.post("/analyze_resume")
async def analyze_resume_route(
    file: UploadFile = File(...),
    job_description: str = Form(""),
    user_id: int = Depends(get_current_user)
):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp:
        temp.write(await file.read())
        temp_path = temp.name

    try:
        if job_description.strip() == "":
            job_description="no job description provided so analyze resume and tailor it as job market"
        data = extract_resume_text(temp_path)

        resume_text = data["resume_data"]
        filename = file.filename

        resume_id = upload_resume(
            user_id=user_id,
            raw_text=resume_text,
            file_name=filename
        )

        response = analyze_resume(
            data=resume_text,
            job_description=job_description
        )

        create_analysis(
        resume_id=resume_id,
        model_id = analyzer_model_id,
        feedback=response["feedback"],
        suggestions=response["suggestions"],
        ats_score=response["ats_score"],
        job_vs_resume_analysis=response["job_vs_resume_analysis"],
        analysis_match_score=response["analysis_match_score"]
        )

        return {
            "resume_id": resume_id,
            **response
        }

    finally:
        os.remove(temp_path)

@router.post("/rewrite_resume")
async def rewrite_resume_route(
    file: UploadFile = File(...),
    job_description: str = Form(""),
    user_id: int = Depends(get_current_user),
    template_id:int = Form(...)
):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp:
        temp.write(await file.read())
        temp_path = temp.name

    try:
        if job_description.strip() == "":
            job_description="no job description provided so analyze resume and tailor it as job market"
        data = extract_resume_text(temp_path)

        resume_text = data["resume_data"]
        filename = file.filename

        resume_id = upload_resume(
            user_id=user_id,
            raw_text=resume_text,
            file_name=filename
        )

        response = rewrite_resume(
        data=resume_text,
        job_description=job_description,
        resume_format=template_id
        )

        create_analysis(
        resume_id=resume_id,
        model_id = analyzer_model_id,
        feedback=response["feedback"],
        suggestions=response["suggestions"],
        ats_score=response["ats_score"],
        job_vs_resume_analysis=response["job_vs_resume_analysis"],
        analysis_match_score=response["analysis_match_score"]
        )

        pdf_path = generate_pdf_from_latex(
            latex_code=response["latex_code"],
            source_file_name=filename,
            resume_id=resume_id
        )

        preview_path = generate_pdf_preview(
            pdf_path=pdf_path,
            resume_id=resume_id,
        )

        preview_img_url = upload_resume_preview(
            image_path=preview_path,
            resume_id=resume_id,
        )

        new_resume_id = save_generated_resume(
            resume_id=resume_id,
            template_id=template_id,
            model_id=rewrite_model_id,
            latex_code=response["latex_code"],
            preview_img_url=preview_img_url,
            pdf_data=Path(pdf_path).read_bytes(),
        )

        

        # Return metadata only
        return {
            "new_resume_id": new_resume_id,
            "resume_id": resume_id,
            "ats_score": response["ats_score"],
            "feedback": response["feedback"],
            "suggestions": response["suggestions"],
            "job_vs_resume_analysis": response[
                "job_vs_resume_analysis"
            ],
            "analysis_match_score": response[
                "analysis_match_score"
            ],
            "pdf_url": f"/generated-resumes/{resume_id}/pdf",
            "preview_img_url": preview_img_url,
        }

    finally:
        os.remove(temp_path)

@router.get("/analysis-history")
async def get_resume_analysis_history(
    user_id: int = Depends(get_current_user),
):
    return get_analysis_history(user_id)


@router.get("/rewrite-history")
async def get_resume_rewrite_history(
    user_id: int = Depends(get_current_user),
):
    return get_rewrite_history(user_id)

@router.get("/generated-resumes/{resume_id}/pdf")
async def get_generated_resume_pdf_route(
    resume_id: int,
    user_id: int = Depends(get_current_user),
):
    pdf_bytes = get_generated_resume_pdf(
        resume_id=resume_id,
        user_id=user_id,
    )

    if pdf_bytes is None:
        raise HTTPException(
            status_code=404,
            detail="Generated resume PDF not found",
        )

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="resume_{resume_id}.pdf"'
        },
    )

@router.get('/templates')
async def send_templates():
    return get_templates()




