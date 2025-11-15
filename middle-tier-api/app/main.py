from fastapi import FastAPI, UploadFile, File, HTTPException
import httpx  # Used to make requests to your AI service
import PyPDF2 # Example library for PDF text extraction
from PyPDF2.errors import PdfReadError
import io
from docx import Document


app = FastAPI(
    title="AI Student Advisor - Middle Tier",
    description="Handles PDF uploads, LLM processing, and data management. \n" \
    "Connecting System",
    version="1.0.0"
)

# URL for your Middle Tier (AI Layer) service
AI_LAYER_URL = "http://your-middle-tier-service-address/extract-from-syllabus"

@app.post("/upload-syllabus/")
async def create_upload_file(file: UploadFile = File(...)):
    """
    1. Receives a syllabus file from the Frontend.
    2. Extracts the raw text.
    3. Sends the raw text to the Middle Tier (AI Layer) for processing.
    """
    
    # Receive File and Extract Text 
    try:
        # Read file contents into memory 
        contents = await file.read()
        
        raw_text = ""
        if file.content_type == "application/pdf":
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(contents))
            for page in pdf_reader.pages:
                raw_text += page.extract_text()
        elif file.filename and file.filename.endswith(".docx"):
            doc = Document(io.BytesIO(contents))
            raw_text = "\n".join([p.text for p in doc.paragraphs])
        else:
            # Assume plain text for other file types for this example will end in error
            raw_text = contents.decode('utf-8')
        

        if not raw_text:
            raise HTTPException(status_code=400, detail="Could not extract text from file.")
    except PdfReadError as e:
        raise HTTPException(status_code=400, detail=f"Invalid PDF file: {e}")
    except UnicodeDecodeError as e:
        raise HTTPException(status_code=400, detail=f"File encoding error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File processing error: {e}")
    
    
