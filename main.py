from fastapi import FastAPI, HTTPException, Path, Query
from pydantic import BaseModel, Field
from typing import Optional, List
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

# MongoDB setup
MONGO_URI = "YOUR_MONGODB_ATLAS_CONNECTION_STRING"
client = AsyncIOMotorClient(MONGO_URI)
db = client["student_management"]
collection = db["students"]

app = FastAPI()

# Helper functions
def student_helper(student) -> dict:
    return {
        "id": str(student["_id"]),
        "name": student["name"],
        "age": student["age"],
        "address": student["address"],
    }

# Request and Response Models
class AddressModel(BaseModel):
    city: str
    country: str

class StudentModel(BaseModel):
    name: str
    age: int
    address: AddressModel

class UpdateStudentModel(BaseModel):
    name: Optional[str]
    age: Optional[int]
    address: Optional[AddressModel]

@app.post("/students", status_code=201)
async def create_student(student: StudentModel):
    student_data = student.dict()
    result = await collection.insert_one(student_data)
    return {"id": str(result.inserted_id)}

@app.get("/students")
async def list_students(
    country: Optional[str] = Query(None),
    age: Optional[int] = Query(None)
):
    query = {}
    if country:
        query["address.country"] = country
    if age:
        query["age"] = {"$gte": age}

    students = await collection.find(query).to_list(100)
    return {"data": [student_helper(student) for student in students]}

@app.get("/students/{id}")
async def get_student(id: str = Path(...)):
    student = await collection.find_one({"_id": ObjectId(id)})
    if student:
        return student_helper(student)
    raise HTTPException(status_code=404, detail="Student not found")

@app.patch("/students/{id}", status_code=204)
async def update_student(id: str, student: UpdateStudentModel):
    update_data = {k: v for k, v in student.dict().items() if v is not None}
    if update_data:
        result = await collection.update_one(
            {"_id": ObjectId(id)}, {"$set": update_data}
        )
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Student not found")
    return {}

@app.delete("/students/{id}", status_code=200)
async def delete_student(id: str):
    result = await collection.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Student not found")
    return {"detail": "Student deleted"}
