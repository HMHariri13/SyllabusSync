#  Backend API Endpoints (Integration Contract)

This document defines all communication between the **Middle-Tier (Client)** and the **Backend (Server)**. All data is transferred as JSON.

---

## 1. Syllabus File Upload

**Purpose:** To send a syllabus PDF/DOCX to the Backend for processing.

| Detail | Specification |
| :--- | :--- |
| **Method** | `POST` |
| **Path** | `/api/upload/syllabus` |
| **Request Payload (Input)** | A file object (e.g., base64 encoded file data) and a user ID. |
| **Success Response (Output)** | `Status: 201 Created` with a JSON body: `{ "status": "success", "message": "Syllabus processing started" }` |
| **Error Response** | `Status: 400 Bad Request` |

---

## 2. Get Student Deadlines

**Purpose:** To retrieve all extracted deadlines for a specific student/course.

| Detail | Specification |
| :--- | :--- |
| **Method** | `GET` |
| **Path** | `/api/deadlines/{course_id}` |
| **Request Payload (Input)** | None (uses course ID from the URL path) |
| **Success Response (Output)** | `Status: 200 OK` with a JSON list of deadlines: `[ { "type": "Exam", "due_date": "2025-12-10", ... }, ... ]` |

---

## 3. Grade Simulation

**Purpose:** To send "what-if" scores and retrieve a predicted final grade.

| Detail | Specification |
| :--- | :--- |
| **Method** | `POST` |
| **Path** | `/api/simulate/grade` |
| **Request Payload (Input)** | JSON body with current scores and simulated scores. |
| **Success Response (Output)** | `Status: 200 OK` with a JSON body: `{ "predicted_grade": "A-", "score_needed_on_final": 88 }` |
