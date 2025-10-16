# SyllabusSync Architecture Overview 

This document explains the roles of the all teams and the path data takes through the system.

##  Team Definitions

* **Team 1: Backend API (The Data Engine)**
    * **Goal:** Manage all data. Processes the syllabus (via LLM) into structured JSON, and interacts directly with the database (DB) for all reading, writing, and querying.
    * **Focus Folder:** `backend-api/`

* **Team 2: Middle-Tier API (The Router)**
    * **Goal:** Sit between the Frontend and Backend. Receives user requests from Team 3 and relays them to the correct Team 1 endpoint. Prepares and sends the final response back to the user.
    * **Focus Folder:** `middle-tier-api/`

* **Team 3: Frontend App (The User Interface)**
    * **Goal:** Build the user-facing application (web or mobile). Handles the display, user input, and making all requests to the Middle-Tier API.
    * **Focus Folder:** `frontend-app/`

---

##  Data Flow: Uploading a Syllabus

This is the path a PDF file takes from the user to the database:

1.  **START:** Team 3 (Frontend) sends the file upload request.
2.  **MIDDLE:** Team 2 (Middle-Tier) receives the request and forwards it to Team 1.
3.  **END (Team 1):** The Backend API takes the file, calls the **LLM** for data extraction, converts the results to structured **JSON**, and then saves it to the **Database**.
4.  **RETURN:** Team 1 sends a success message back through Team 2 to Team 3.

---
