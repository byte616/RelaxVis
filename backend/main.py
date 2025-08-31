from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
import parser

app = FastAPI()

# allow the frontend to access the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # development only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    # save file to uploads/
    with open(f"uploads/{file.filename}", "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    print(f"file save: {file.filename}")

    # run parser
    success = parser.parse(f"uploads/{file.filename}")
    if not success:
        return {"error": "Failed to parse the file."}
    return {"filename": file.filename}
