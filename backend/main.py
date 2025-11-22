from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from backend.core.database import engine, Base, get_db
from backend.models.models import User
from backend.api import users, auth, jobs
from backend.api.auth import verify_password, create_access_token
from backend.services.kafka_service import kafka_service
from datetime import timedelta
from backend.core.config import settings

from fastapi.middleware.cors import CORSMiddleware

# Create tables (for simplicity in dev, usually use alembic)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Multi-Agent Research Platform")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(jobs.router, prefix="/jobs", tags=["jobs"])

@app.on_event("startup")
async def startup_event():
    kafka_service.start()

@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/")
def read_root():
    return {"message": "Welcome to the Multi-Agent Research Platform API"}
