import cloudinary

from src.services.settings import Settings


def cloudinary_init():
    settings = Settings()
    CLOUDINARY_CLOUD_NAME = settings.CLOUDINARY_CLOUD_NAME
    CLOUDINARY_PUBLIC_API_KEY = settings.CLOUDINARY_PUBLIC_API_KEY
    CLOUDINARY_SECRET_API_KEY = settings.CLOUDINARY_SECRET_API_KEY

    cloudinary.config(
        cloud_name=CLOUDINARY_CLOUD_NAME,
        api_key=CLOUDINARY_PUBLIC_API_KEY,
        api_secret=CLOUDINARY_SECRET_API_KEY,
        secure=True,
    )
