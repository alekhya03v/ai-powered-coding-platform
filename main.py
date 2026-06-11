import os
from datetime import datetime, timezone
from typing import Optional, List

from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Text, JSON, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker, Session

from generator import generate_solution

# 1. Database setup
load_dotenv()

SQLALCHEMY_DATABASE_URL = "sqlite:///./dsa.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Problem(Base):
    __tablename__ = "problems"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String, index=True)
    description = Column(Text)
    source = Column(String, default="manual")
    generated = Column(JSON, nullable=True)
    pattern = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

Base.metadata.create_all(bind=engine)

# 2. FastAPI app setup
app = FastAPI()

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Dependencies & Pydantic Models
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class ProblemCreate(BaseModel):
    title: Optional[str] = None
    description: str

class ProblemSummary(BaseModel):
    id: int
    title: Optional[str] = None
    pattern: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

# 4. Endpoints

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/problems")
def create_problem(problem_in: ProblemCreate, db: Session = Depends(get_db)):
    # Prevent duplicate saves: exact title match (if provided) or exact description match
    existing_problem = None
    if problem_in.title:
        existing_problem = db.query(Problem).filter(Problem.title == problem_in.title).first()
    
    if not existing_problem:
        existing_problem = db.query(Problem).filter(Problem.description == problem_in.description).first()
        
    if existing_problem:
        return existing_problem

    # Prepare text for the generator
    if problem_in.title:
        problem_text = f"Title: {problem_in.title}\n\nDescription:\n{problem_in.description}"
    else:
        problem_text = problem_in.description
        
    # Generate solution
    generated_data = generate_solution(problem_text)
    
    # Try to extract title if one wasn't provided but is available in generated output
    final_title = problem_in.title
    if not final_title and not generated_data.get("error"):
        final_title = generated_data.get("title")
    
    # Store in database
    db_problem = Problem(
        title=final_title,
        description=problem_in.description,
        source="manual",
        generated=generated_data
    )
    db.add(db_problem)
    db.commit()
    db.refresh(db_problem)
    
    return db_problem

@app.get("/problems", response_model=List[ProblemSummary])
def get_problems(db: Session = Depends(get_db)):
    # Fetch only the needed summary columns to avoid pulling heavy JSON objects
    problems = db.query(Problem.id, Problem.title, Problem.pattern, Problem.created_at).all()
    return [
        {
            "id": p.id, 
            "title": p.title, 
            "pattern": p.pattern, 
            "created_at": p.created_at
        } for p in problems
    ]

@app.get("/problems/{problem_id}")
def get_problem(problem_id: int, db: Session = Depends(get_db)):
    problem = db.query(Problem).filter(Problem.id == problem_id).first()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    return problem

@app.delete("/problems/{problem_id}")
def delete_problem(problem_id: int, db: Session = Depends(get_db)):
    problem = db.query(Problem).filter(Problem.id == problem_id).first()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    db.delete(problem)
    db.commit()
    return {"status": "deleted", "id": problem_id}
