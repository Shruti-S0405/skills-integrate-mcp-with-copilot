"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""


from pydantic import BaseModel, EmailStr
class Activity(BaseModel):
    name: str
    description: str
    schedule: str
    max_participants: int
    participants: list[EmailStr] = []

class ActivityCreate(BaseModel):
    name: str
    description: str
    schedule: str
    max_participants: int

class Signup(BaseModel):
    activity_name: str
    email: EmailStr

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# In-memory activity database
activities: dict[str, Activity] = {
    "Chess Club": Activity(
        name="Chess Club",
        description="Learn strategies and compete in chess tournaments",
        schedule="Fridays, 3:30 PM - 5:00 PM",
        max_participants=12,
        participants=["michael@mergington.edu", "daniel@mergington.edu"]
    ),
    # ...more activities...
}


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    return {name: activity.dict() for name, activity in activities.items()}


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    activity = activities[activity_name]
    if email in activity.participants:
        raise HTTPException(status_code=400, detail="Student is already signed up")
    if len(activity.participants) >= activity.max_participants:
        raise HTTPException(status_code=400, detail="Activity is full")
    activity.participants.append(email)
    return {"message": f"Signed up {email} for {activity_name}"}


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str):
    """Unregister a student from an activity"""
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")
    activity = activities[activity_name]
    if email not in activity.participants:
        raise HTTPException(status_code=400, detail="Student is not signed up for this activity")
    activity.participants.remove(email)
    return {"message": f"Unregistered {email} from {activity_name}"}
# Add this above the existing endpoints
from fastapi import Body

@app.post("/activities/create")
def create_activity(activity: dict = Body(...)):
    """Create a new activity"""
    name = activity.get("name")
    if not name or name in activities:
        raise HTTPException(status_code=400, detail="Activity name missing or already exists")
    new_activity = Activity(
        name=name,
        description=activity.get("description", ""),
        schedule=activity.get("schedule", ""),
        max_participants=activity.get("max_participants", 0),
        participants=[]
    )
    activities[name] = new_activity
    return {"message": f"Activity '{name}' created successfully"}
