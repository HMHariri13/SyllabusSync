from fastapi import FastAPI, UploadFile, File, HTTPException
import httpx  # Used to make requests to your AI service
import PyPDF2 # Example library for PDF text extraction
from PyPDF2.errors import PdfReadError
import io
from docx import Document
from fastapi.responses import JSONResponse
import pdfplumber
from openai import OpenAI
import os
from .database import syllabi_collection, tasks_collection
from .models import SyllabusCreate, Syllabus, ManualTaskCreate, ManualTaskUpdate
from datetime import datetime, timezone
from bson import ObjectId
from dotenv import load_dotenv
import json
import re
from fastapi.middleware.cors import CORSMiddleware #for handling frontend and backend connection


load_dotenv()

app = FastAPI(
    title="AI Student Advisor - Middle Tier",
    description="Handles PDF uploads, LLM processing, and data management. \n" \
    "Connecting System",
    version="1.0.0"
)

#Frontend to backend connection handling
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def clean_llm_json_response(raw: str) -> dict:
    """
    Cleans LLM response and returns a parsed JSON object (dict).
    """
    # Remove ```json ... ``` fences
    raw = re.sub(r"```json", "", raw, flags=re.IGNORECASE)
    raw = re.sub(r"```", "", raw)
    raw = raw.strip()
    
    # Parse into a Python dictionary
    try:
        data_dict = json.loads(raw)
        return data_dict
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse LLM response as JSON: {e}")

# URL for your Middle Tier (AI Layer) service
AI_LAYER_URL = "http://your-middle-tier-service-address/extract-from-syllabus"

# -----------------------------
# Upload endpoint
# -----------------------------
@app.post("/upload-syllabus/")
async def create_upload_file(file: UploadFile = File(...)):
    """
    1. Receives a syllabus file from the Frontend.
    2. Extracts the raw text.
    3. Sends the raw text to API for processing.
    """
    
    # Read file contents into memory 
    contents = await file.read()

    # -----------------------------
    # File size limit (5 MB)
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large (limit 5MB).")
    # -----------------------------

    # Receive File and Extract Text 
    try:
        raw_text = ""
        if file.content_type == "application/pdf":
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(contents))
            for page in pdf_reader.pages:
                raw_text += page.extract_text() or ""
        elif file.filename and file.filename.endswith(".docx"):
            doc = Document(io.BytesIO(contents))
            raw_text = "\n".join([p.text for p in doc.paragraphs])
        else:
            # Assume plain text for other file types
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
    prompt = """
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
          "sourceText": "string"
        }
      ],
      "topics": [
        {"week": "number|null", "title": "string", "readings": ["string"]}
      ]
    }
    Syllabus text:
    """ + f"\n{raw_text[:12000]}" # limit to avoid token overload

    # Call OpenAI
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    # Send to OpenAI for structured extraction
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # you can change to gpt-4.1 or gpt-4o
            messages=[
                {"role": "system", "content": "You extract structured academic deadlines from text."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            response_format={"type": "json_object"} 
        )
        result = response.choices[0].message.content or ""
        structured_data = clean_llm_json_response(result)

    except Exception as e:
        '''return JSONResponse(
            {"error": f"OpenAI API request failed: {e}"},
            status_code=500
        ) replace it by the structure of data below.'''
        structured_data = {
            "error": f"OpenAI API request failed: {e}",
            "tasks": [],
            "topics": []
        }

    # Insert into Mongo
    uploaded_at = datetime.now(timezone.utc)

    doc = {
        "filename": file.filename,
        "contentType": file.content_type,
        "rawText": raw_text,
        "structured": structured_data,
        "uploadedAt": uploaded_at,
    }

    try:
        insert_result = syllabi_collection.insert_one(doc)
    except Exception as e:
        raise HTTPException(status_code = 500, detail=f"MOngodB INSERT FAILED:{e}")

    # Return inserted ID
    return {
        "id": str(insert_result.inserted_id),
        "filename": file.filename,
        "uploadedAt": uploaded_at.isoformat(),
        "structured": structured_data,
    }
     #structured_data = clean_llm_json_response(result)
    #Return structured JSON
    #return JSONResponse({"structured_data": result})
    #return structured_data

@app.post("/syllabi", response_model=Syllabus)
def create_syllabus_entry(syllabus: SyllabusCreate):
    # 1. Convert Pydantic model -> dict
    doc = syllabus.model_dump()  # {'userId', 'courseName', 'term', 'rawText'}

    # 2. Add timestamp
    uploadedAt = datetime.utcnow()
    doc["uploadedAt"] = uploadedAt

    # 3. Insert into MongoDB
    result = syllabi_collection.insert_one(doc)

    # 4. Build Syllabus response
    return Syllabus(
        id=str(result.inserted_id),
        **doc,            # includes uploadedAt, userId, courseName, term, rawText
    )

@app.get("/syllabi/{syllabus_id}", response_model=Syllabus)
def get_syllabus_entry(syllabus_id: str):
    try:
        oid = ObjectId(syllabus_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid syllabus id format")

    doc = syllabi_collection.find_one({"_id": oid})
    if not doc:
        raise HTTPException(status_code=404, detail="Syllabus not found")

    doc["_id"] = str(doc["_id"])
    doc.pop("_id", None)
    return Syllabus(**doc)

#Temporary in-memory store (replace with DB later)
CALENDAR_EVENTS = []

@app.post("/calendar/import")
async def import_events(structured_data: dict):
    """
    Accepts structured syllabus JSON and converts tasks into calendar events
    """
    events = []

    for task in structured_data.get("tasks", []):
        if task.get("dueAt"):
            events.append({
                "title": task["title"],
                "type": task["type"],
                "start": task["dueAt"],
                "description": task.get("description"),
            })

    CALENDAR_EVENTS.extend(events)
    return {"added": len(events)}


@app.get("/calendar/events")
async def get_calendar_events():
    return CALENDAR_EVENTS
    
@app.post("/syllabi/{syllabus_id}/tasks")
async def save_tasks_for_syllabus(syllabus_id: str, structured_data: dict):
    """
    Persist extracted tasks for a given syllabus into MongoDB.

    - `syllabus_id` should be the ID returned from POST /syllabi.
    - `structured_data` is the JSON returned by /upload-syllabus/ (or the LLM),
      containing a `tasks` array.
    """
    try:
        oid = ObjectId(syllabus_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid syllabus id format")

    syllabus_doc = syllabi_collection.find_one({"_id": oid})
    if not syllabus_doc:
        raise HTTPException(status_code=404, detail="Syllabus not found")

    tasks = structured_data.get("tasks", [])
    if not tasks:
        return {"inserted": 0}

    docs_to_insert = []
    for task in tasks:
        docs_to_insert.append(
            {
                "syllabusId": syllabus_id,
                "type": task.get("type"),
                "title": task.get("title"),
                "dueAt": task.get("dueAt"),
                "window": task.get("window"),
                "points": task.get("points"),
                "weightPct": task.get("weightPct"),
                "description": task.get("description"),
                "sourceText": task.get("sourceText"),
            }
        )

    if not docs_to_insert:
        return {"inserted": 0}

    result = tasks_collection.insert_many(docs_to_insert)
    return {"inserted": len(result.inserted_ids)}


# -----------------------------
# Manual task insert & update (when syllabus doesn't list all assignments)
# -----------------------------

@app.get("/syllabi/{syllabus_id}/tasks")
async def get_tasks_for_syllabus(syllabus_id: str):
    """
    List all tasks (assignments, due dates, etc.) for a syllabus.
    Use this to show what's stored and to support edit/update flows.
    """
    try:
        oid = ObjectId(syllabus_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid syllabus id format")

    syllabus_doc = syllabi_collection.find_one({"_id": oid})
    if not syllabus_doc:
        raise HTTPException(status_code=404, detail="Syllabus not found")

    cursor = tasks_collection.find({"syllabusId": syllabus_id}).sort("dueAt", 1)
    tasks = []
    for doc in cursor:
        doc["id"] = str(doc.pop("_id"))
        tasks.append(doc)
    return {"tasks": tasks}


@app.post("/syllabi/{syllabus_id}/tasks/manual")
async def add_manual_task(syllabus_id: str, task: ManualTaskCreate):
    """
    Manually add a single task (assignment, exam, etc.) for a syllabus
    when the syllabus doesn't include it or the user wants to add more.
    """
    try:
        oid = ObjectId(syllabus_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid syllabus id format")

    syllabus_doc = syllabi_collection.find_one({"_id": oid})
    if not syllabus_doc:
        raise HTTPException(status_code=404, detail="Syllabus not found")

    doc = {
        "syllabusId": syllabus_id,
        "type": task.type,
        "title": task.title,
        "dueAt": task.dueAt,
        "window": task.window.model_dump() if task.window else None,
        "points": task.points,
        "weightPct": task.weightPct,
        "description": task.description,
        "sourceText": task.sourceText,
    }
    result = tasks_collection.insert_one(doc)
    return {"id": str(result.inserted_id), "inserted": 1}


@app.put("/tasks/{task_id}")
async def update_task(task_id: str, task: ManualTaskCreate):
    """
    Full update of an existing task. Send all fields you want to keep.
    """
    try:
        oid = ObjectId(task_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid task id format")

    existing = tasks_collection.find_one({"_id": oid})
    if not existing:
        raise HTTPException(status_code=404, detail="Task not found")

    update_doc = {
        "type": task.type,
        "title": task.title,
        "dueAt": task.dueAt,
        "window": task.window.model_dump() if task.window else None,
        "points": task.points,
        "weightPct": task.weightPct,
        "description": task.description,
        "sourceText": task.sourceText,
    }
    tasks_collection.update_one({"_id": oid}, {"$set": update_doc})
    return {"id": task_id, "updated": 1}


@app.patch("/tasks/{task_id}")
async def patch_task(task_id: str, task: ManualTaskUpdate):
    """
    Partial update of an existing task. Only send fields you want to change.
    """
    try:
        oid = ObjectId(task_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid task id format")

    existing = tasks_collection.find_one({"_id": oid})
    if not existing:
        raise HTTPException(status_code=404, detail="Task not found")

    update_doc = task.model_dump(exclude_unset=True)
    # Pydantic serializes nested TaskWindow to dict; ensure no BaseModel in payload
    if "window" in update_doc and hasattr(update_doc["window"], "model_dump"):
        update_doc["window"] = update_doc["window"].model_dump()
    tasks_collection.update_one({"_id": oid}, {"$set": update_doc})
    return {"id": task_id, "updated": 1}


@app.delete("/tasks/{task_id}")
async def delete_task(task_id: str):
    """Remove a task (e.g. one that was added manually by mistake)."""
    try:
        oid = ObjectId(task_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid task id format")

    result = tasks_collection.delete_one({"_id": oid})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"id": task_id, "deleted": 1}
