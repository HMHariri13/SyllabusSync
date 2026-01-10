# Backend API
#This is where the code for LLM processing, data extraction, and database interaction lives.

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import pdfplumber
from openai import OpenAI
import os


#Initializing app
app = FastAPI(title="Syllabus Deadline Extractor API")

#Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))  # <-- set your API key in environment

@app.post("/upload")
async def upload_syllabus(file: UploadFile = File(...)):
    """
    Upload a syllabus PDF, extract its text, and return structured deadlines from OpenAI.
    """

    #Check file type
    if not file.filename.endswith(".pdf"):
        return JSONResponse(
            {"error": "Please upload a PDF file."},
            status_code=400
        )

    #Extract text from PDF
    try:
        with pdfplumber.open(file.file) as pdf:
            text = "\n".join(page.extract_text() or "" for page in pdf.pages)
    except Exception as e:
        return JSONResponse(
            {"error": f"Failed to read PDF: {e}"},
            status_code=500
        )

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
    {text[:12000]}  # limit to avoid token overload
    """

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


#To run: uvicorn main:app --reload
