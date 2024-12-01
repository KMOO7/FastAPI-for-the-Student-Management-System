from fastapi import FastAPI, HTTPException, Path, Query
from pydantic import BaseModel
from typing import List, Optional
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient
import os

# Initialize FastAPI app
app = FastAPI()

# MongoDB setup
MONGO_URI = os.getenv("MONGO_URI", "your_mongodb_connection_string")
client = AsyncIOMotorClient(MONGO_URI)
db = client.student_management
students_collection = db.students

# Pydantic models
class Address(BaseModel):
    city: str
    country: str

class Student(BaseModel):
    name: str
    age: int
    address: Address

class StudentUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    address: Optional[Address] = None

# Root endpoint to prevent "Not Found" error
@app.get("/")
async def read_root():
    return {"message": "Welcome to the Student Management System API!"}

# Create a student
@app.post("/students", status_code=201)
async def create_student(student: Student):
    student_dict = student.dict()
    result = await students_collection.insert_one(student_dict)
    return {"id": str(result.inserted_id)}

# List students with optional filters
@app.get("/students", status_code=200)
async def list_students(
    country: Optional[str] = Query(None),
    age: Optional[int] = Query(None)
):
    query = {}
    if country:
        query["address.country"] = country
    if age:
        query["age"] = {"$gte": age}
    students = await students_collection.find(query).to_list(100)
    return {"data": students}

# Fetch a student by ID
@app.get("/students/{id}", status_code=200)
async def fetch_student(id: str = Path(...)):
    student = await students_collection.find_one({"_id": ObjectId(id)})
    if student:
        student["_id"] = str(student["_id"])
        return student
    raise HTTPException(status_code=404, detail="Student not found")

# Update a student by ID
@app.patch("/students/{id}", status_code=204)
async def update_student(id: str, student_update: StudentUpdate):
    update_data = {k: v for k, v in student_update.dict().items() if v is not None}
    if update_data:
        result = await students_collection.update_one(
            {"_id": ObjectId(id)}, {"$set": update_data}
        )
        if result.modified_count:
            return
    raise HTTPException(status_code=404, detail="Student not found")

# Delete a student by ID
@app.delete("/students/{id}", status_code=200)
async def delete_student(id: str):
    result = await students_collection.delete_one({"_id": ObjectId(id)})
    if result.deleted_count:
        return {"message": "Student deleted"}
    raise HTTPException(status_code=404, detail="Student not found")
