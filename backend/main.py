from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
import parser
import json

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
    save_path = f"uploads/{file.filename}"
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    print(f"file save: {file.filename}")

    # run parser
    success = parser.parse(f"uploads/{file.filename}")
    if not success:
        return {"error": "Failed to parse the file."}
    
    # check if json exists 
    json_path = f"{save_path}.json"
    if not os.path.exists(json_path):
        return {"error": f"JSON not found: {json_path}"}
    
    # load json data
    with open(json_path, "r", encoding="utf-8") as f:
        graph_data = json.load(f)

    return {
        "filename": file.filename, 
        "graph": graph_data
    }
