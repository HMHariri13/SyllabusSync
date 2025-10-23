from fastapi import FastAPI

app = FastAPI(
    title="AI Student Advisor - Middle Tier",
    description="Handles PDF uploads, LLM processing, and data management. \n" \
    "Connecting System",
    version="1.0.0"
)

@app.get("/upload_syllabus")
async def uploaded( Syllabus_file: uploaded = file("name_of_file")):
    try:
        pdf_bytes = await syllabus_file.read()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading uploaded file: {e}")
    files_to_send = {
        'pdf_file': (syllabus_file.filename, pdf_bytes, syllabus_file.content_type)
    }
    
