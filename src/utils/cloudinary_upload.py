from http import HTTPStatus

from cloudinary.uploader import upload
from fastapi import HTTPException, UploadFile

from . import cloudinary_init


async def upload_image(image: UploadFile):
    cloudinary_init()
    try:
        upload_result = upload(image.file)
        file_url = upload_result['secure_url']
        return file_url
    except Exception as e:
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            detail=f'Error on image upload: {e}',
        )
