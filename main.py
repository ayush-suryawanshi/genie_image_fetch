from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
import shutil
import os
import zipfile

app = FastAPI()

# Folder to store uploaded images
UPLOAD_FOLDER = "uploaded_images" # Replace with actual folder path . 
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.post("/upload/")
async def upload_image(file_name:str,file: UploadFile = File(...)): # Upload an image and save it with a unique ID.

    file_ext = file.filename.split(".")[-1]
    unique_filename = f"{file_name}.{file_ext}"
    file_path = os.path.join(UPLOAD_FOLDER, unique_filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {"image_id": unique_filename, "message": "Image uploaded successfully"}

@app.get("/images/")
async def list_images(): # Get a list of all uploaded image filenames.
    images = os.listdir(UPLOAD_FOLDER)
    if not images:
        raise HTTPException(status_code=404, detail="No images found")
    return {"images": images}

@app.get("/image/{image_id}")
async def get_image(image_id: str): # Retrieve a specific image by its ID.
    image_path = os.path.join(UPLOAD_FOLDER, image_id+'.webp')
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Image not found")
    
    return FileResponse(image_path, media_type="image/jpeg")

@app.get("/all-images/")
async def download_all_images(): # Returns all images as a ZIP file.

    images = os.listdir(UPLOAD_FOLDER)
    if not images:
        raise HTTPException(status_code=404, detail="No images found")

    zip_path = "all_images.zip"
    
    with zipfile.ZipFile(zip_path, "w") as zipf:
        for image in images:
            zipf.write(os.path.join(UPLOAD_FOLDER, image), arcname=image)

    return FileResponse(zip_path, media_type="application/zip", filename="all_images.zip")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
