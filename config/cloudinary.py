from dotenv import load_dotenv
import os

load_dotenv()

import cloudinary

cloudinary.config( 
  cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME"), 
  api_key = os.getenv("CLOUDINARY_API_KEY"), 
  api_secret = os.getenv("CLOUDINARY_API_SECRET"),
#   secure_distribution = "mydomain.com",
#   upload_prefix = "myprefix"
)
import cloudinary.uploader
import cloudinary.api
from cloudinary import CloudinaryImage

#--reference--
# cloudinary.uploader.upload("dog.mp4", 
#   asset_folder = "pets", 
#   public_id = "my_dog",
#   overwrite = True, 
#   notification_url = "https://mysite.example.com/notify_endpoint", 
#   resource_type = "video")
