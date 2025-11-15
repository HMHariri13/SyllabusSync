from fastapi import FastAPI, UploadFile, File, HTTPException
import httpx  # Used to make requests to your AI service
import PyPDF2 # Example library for PDF text extraction
from PyPDF2.errors import PdfReadError
import io
from docx import Document
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import pdfplumber
from openai import OpenAI
import os


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
    3. Sends the raw text to API for processing.
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

  #Build prompt for OpenAI
    prompt = f"""
    You are a helpful assistant that extracts academic deadlines from a syllabus.
    The syllabus text is below.
    Please output a JSON with this structure:

    {
      "course": {
        "code": "string",
        "title": "string",
        "term": "string",
        "instructor": "string|null",
        "meeting": "string|null"
      },
      "tasks": [
        {
          "type": "HOMEWORK|PROJECT|EXAM|QUIZ|READING|OTHER",
          "title": "string",
          "dueAt": "YYYY-MM-DDTHH:mm:ssZ|null",
          "window": {"start":"YYYY-MM-DDTHH:mm:ssZ|null","end":"YYYY-MM-DDTHH:mm:ssZ|null"},
          "points": "number|null",
          "weightPct": "number|null",
          "description": "string|null",
          "sourceText": "string"       // short quote for traceability
        }
      ],
      "topics": [
        {"week": "number|null", "title": "string", "readings": ["string"]}
      ]
    }


    Syllabus text:
    {raw_text[:12000]}  # limit to avoid token overload
    """
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    #Send to OpenAI for structured extraction
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # you can change to gpt-4.1 or gpt-4o
            messages=[
                {"role": "system", "content": "You extract structured academic deadlines from text."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
        )
        result = response.choices[0].message.content
    except Exception as e:
        return JSONResponse(
            {"error": f"OpenAI API request failed: {e}"},
            status_code=500
        )

    #Return structured JSON
    return JSONResponse({"structured_data": result})







    
