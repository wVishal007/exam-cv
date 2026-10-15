import cloudinary.uploader


def upload_resume_preview(
    image_path: str,
    resume_id: int,
) -> str:
    result = cloudinary.uploader.upload(
        image_path,
        folder="resume-previews",
        public_id=f"resume_{resume_id}",
        resource_type="image",
        overwrite=True,
    )

    return result["secure_url"]