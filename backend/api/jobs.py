from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List
import shutil
import os
from backend.core.database import get_db
from backend.models.models import Job, User, Report
from backend.api.auth import get_current_active_user
from backend.services.agent import agent_service
from backend.services.kafka_service import kafka_service
from pydantic import BaseModel
from datetime import datetime
from fastapi.responses import StreamingResponse
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

router = APIRouter()

class JobCreate(BaseModel):
    topic: str

class JobOut(BaseModel):
    id: int
    topic: str
    status: str
    created_at: datetime
    result: dict | None = None
    file_path: str | None = None # Added file_path to JobOut

    class Config:
        orm_mode = True

@router.post("/", response_model=JobOut)
async def create_job(
    background_tasks: BackgroundTasks, # Keep background_tasks as a parameter
    topic: str = Form(...),
    file: UploadFile = File(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    file_path = None
    if file:
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

    db_job = Job(topic=topic, file_path=file_path, user_id=current_user.id, status="pending")
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    
    # Publish event
    kafka_service.publish_event("agent.job.events", {
        "job_id": db_job.id, 
        "status": "created", 
        "timestamp": str(datetime.now())
    })
    
    # Trigger background task
    background_tasks.add_task(agent_service.run_job, db_job.id)
    
    return db_job

@router.get("/", response_model=List[JobOut])
def read_jobs(
    skip: int = 0, 
    limit: int = 100, 
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    jobs = db.query(Job).filter(Job.user_id == current_user.id).offset(skip).limit(limit).all()
    return jobs

@router.get("/{job_id}", response_model=JobOut)
def read_job(
    job_id: int, 
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    job = db.query(Job).filter(Job.id == job_id, Job.user_id == current_user.id).first()
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@router.get("/{job_id}/download")
def download_report(job_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    report = db.query(Report).filter(Report.job_id == job.id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, height - 50, report.title)
    
    p.setFont("Helvetica", 12)
    y = height - 80
    for line in report.content.split('\n'):
        if y < 50:
            p.showPage()
            y = height - 50
        p.drawString(50, y, line)
        y -= 15
        
    p.save()
    buffer.seek(0)
    
    return StreamingResponse(
        buffer, 
        media_type="application/pdf", 
        headers={"Content-Disposition": f"attachment; filename=report_{job_id}.pdf"}
    )
