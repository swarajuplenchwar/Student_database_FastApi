from fastapi import FastAPI, HTTPException, Query, Path, Body
from pymongo import MongoClient
from bson import ObjectId
from pydantic import BaseModel

app = FastAPI()

# MongoDB connection
MONGODB_URL = "mongodb+srv://admin:admin123@student.mg8qyok.mongodb.net/"
client = MongoClient(MONGODB_URL)
db = client["library"]
collection = db["students"]

# Schema for student
class Address(BaseModel):
    city: str
    country: str

class Student(BaseModel):
    name: str
    age: int
    address: Address 

# Create a student
@app.post("/students/", status_code=201)
async def create_student(student: Student = Body(...)):
    student_data = student.dict()
    result = collection.insert_one(student_data)
    return {"id": str(result.inserted_id)},"swaraj"

# Get a student by ID
@app.get("/students/{student_id}", response_model=Student)
async def get_student(student_id: str = Path(..., title="The ID of the student previously created")):
    student = collection.find_one({"_id": ObjectId(student_id)})
    if student:
        return student
    else:
        raise HTTPException(status_code=404, detail="Student not found")

# Update a student by ID
@app.patch("/students/{student_id}", status_code=204)
async def update_student(student_id: str = Path(..., title="The ID of the student previously created"), student: Student = Body(...)):
    student_data = student.dict(exclude_unset=True)  # Exclude unset fields
    result = collection.update_one({"_id": ObjectId(student_id)}, {"$set": student_data})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Student not found")

# Delete a student by ID
@app.delete("/students/{student_id}", status_code=200)
async def delete_student(student_id: str = Path(..., title="The ID of the student previously created")):
    result = collection.delete_one({"_id": ObjectId(student_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Student not found")

# Get all students with optional filters
@app.get("/students/", response_model=list[Student])
async def get_all_students(country: str = Query(None, description="To apply filter of country. If not given or empty, this filter should not be applied."),
                           age: int = Query(None, description="Only records which have age greater than equal to the provided age should be present in the result. If not given or empty, this filter should not be applied.")):
    filters = {}
    if country:
        filters["address.country"] = country
    if age:
        filters["age"] = {"$gte": age}
    
    students = []
    for student in collection.find(filters):
        students.append(student)
    return students
