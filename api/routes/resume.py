from api.controllers.resume import analyze_resume,rewrite_resume
from api.routes.auth import get_current_user
from database.operations.upload_resume import upload_resume
from database.operations.generate_resume import save_generated_resume
from utils.pdf_read import extract_resume_text
from database.operations.resume_analysis import create_analysis
from fastapi import APIRouter, UploadFile, Depends, File, Form
import tempfile
import os

router = APIRouter()


@router.post("/analyze_resume")
async def analyze_resume_route(
    file: UploadFile = File(...),
    job_description: str = Form(...),
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
    job_description: str = Form(...),
    resume_format: int = Form(...),
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

        response = rewrite_resume(
        data=resume_text,
        job_description=job_description,
        resume_format=resume_format
        )

        create_analysis(
        resume_id=resume_id,
        feedback=response["feedback"],
        suggestions=response["suggestions"],
        ats_score=response["ats_score"],
        job_vs_resume_analysis=response["job_vs_resume_analysis"],
        analysis_match_score=response["analysis_match_score"]
        )

        save_generated_resume(resume_id,response["latex_code"])

        return {
            "resume_id": resume_id,
            **response
        }

    finally:
        os.remove(temp_path)

