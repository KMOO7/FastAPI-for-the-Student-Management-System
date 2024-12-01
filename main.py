from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

# Create the FastAPI app
app = FastAPI()

# Data model for a student
class Student(BaseModel):
    id: int
    name: str
    age: int
    grade: str
    email: Optional[str] = None

# Simulated database (in-memory)
students_db = []

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Student Management System!"}

# Get all students
@app.get("/students", response_model=List[Student])
async def get_students():
    return students_db

# Get a student by ID
@app.get("/students/{student_id}", response_model=Student)
async def get_student(student_id: int):
    for student in students_db:
        if student.id == student_id:
            return student
    raise HTTPException(status_code=404, detail="Student not found")

# Add a new student
@app.post("/students", response_model=Student)
async def add_student(student: Student):
    students_db.append(student)
    return student

# Update a student
@app.put("/students/{student_id}", response_model=Student)
async def update_student(student_id: int, updated_student: Student):
    for index, student in enumerate(students_db):
        if student.id == student_id:
            students_db[index] = updated_student
            return updated_student
    raise HTTPException(status_code=404, detail="Student not found")

# Delete a student
@app.delete("/students/{student_id}")
async def delete_student(student_id: int):
    for index, student in enumerate(students_db):
        if student.id == student_id:
            del students_db[index]
            return {"message": f"Student with ID {student_id} deleted"}
    raise HTTPException(status_code=404, detail="Student not found")

