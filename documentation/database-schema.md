# Data Schema
The structure and blueprint for all tables and data fields. Details every database table, field name, and data type


# ========================================
# Table: users
# Description: Stores user account information.
# ========================================
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,       # Used for login, unique
    password_hash TEXT NOT NULL,      
    created_at TIMESTAMP DEFAULT NOW()
);

# ========================================
# Table: syllabus
# Description: Stores uploaded syllabus files and metadata.
# ========================================
CREATE TABLE syllabus (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE CASCADE, # Foreign key to the user
    course_name TEXT NOT NULL,                          # e.g., "Intro to Computer Science"
    term TEXT,                                          # e.g., "Fall 2025"
    raw_text TEXT,                                      # The full text extracted from the file
    uploaded_at TIMESTAMP DEFAULT NOW()
);

# ========================================
# Table: deadlines
# Description: Stores individual tasks and deadlines extracted from each syllabus.
# ========================================
CREATE TABLE deadlines (
    id SERIAL PRIMARY KEY,
    syllabus_id INT REFERENCES syllabus(id) ON DELETE CASCADE, # Foreign key to the syllabus
    task_type TEXT,                                           # e.g., "Assignment", "Exam", "Quiz"
    task_name TEXT,                                           # e.g., "Homework 1", "Midterm Exam"
    due_date DATE,                                            # The date the task is due
    weight TEXT,                                              # e.g., "15%", "100 points"
    notes TEXT                                                # Any extra notes from the LLM
);