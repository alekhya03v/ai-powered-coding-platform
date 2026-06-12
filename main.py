import os
import re
import requests
import json
from datetime import datetime, timezone
from typing import Optional, List

from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Text, JSON, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker, Session, relationship

from generator import generate_solution, classify_pattern, suggest_questions

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
    difficulty = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class SubPattern(Base):
    __tablename__ = "sub_patterns"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    pattern = Column(String, index=True) 
    name = Column(String)
    description = Column(String, nullable=True)
    
    questions = relationship("SyllabusQuestion", back_populates="sub_pattern", cascade="all, delete-orphan")

class SyllabusQuestion(Base):
    __tablename__ = "syllabus_questions"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    sub_pattern_id = Column(Integer, ForeignKey("sub_patterns.id"))
    question_title = Column(String)
    difficulty = Column(String, nullable=True)
    completed = Column(Boolean, default=False)
    linked_problem_id = Column(Integer, ForeignKey("problems.id"), nullable=True)
    
    sub_pattern = relationship("SubPattern", back_populates="questions")

Base.metadata.create_all(bind=engine)

# Migration: ensure 'notes' and 'difficulty' columns exist for older DBs
from sqlalchemy import text
with engine.connect() as conn:
    try:
        conn.execute(text("ALTER TABLE problems ADD COLUMN notes TEXT"))
        conn.commit()
    except Exception:
        pass # Column already exists
    try:
        conn.execute(text("ALTER TABLE problems ADD COLUMN difficulty VARCHAR"))
        conn.commit()
    except Exception:
        pass # Column already exists

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Seed Syllabus
SYLLABUS_SKELETON = {
    "Arrays": ["Two-Pointer", "Sliding Window", "Prefix Sum", "Kadane's"],
    "Strings": ["Two-Pointer Palindrome", "Sliding Window"],
    "Binary Search": ["Classic", "Lower/Upper Bound", "Binary Search on Answers", "Search in 2D Matrix"],
    "Stack": ["Monotonic Stack", "Expression Evaluation", "Stack Simulation", "Parenthesis & Scoring", "Stack Design", "Stack + Greedy"],
    "Recursion": ["Linear", "Non-Linear", "Divide & Conquer", "Subsequences"],
    "Linked List": ["Basic Operations", "Fast & Slow Pointers", "Reversal", "Merge/Sort"],
    "Hashing": ["Frequency Map", "Prefix-Sum with Map", "Sliding Window + HashMap"],
    "Heap": ["Top-K", "Merge K Sorted", "Heap with Sliding Window", "Huffman"],
    "Trees": ["DFS Traversals", "BFS/Level-Order", "Lowest Common Ancestor", "Serialization"],
    "BST": ["BST Operations", "LCA & Range Queries"],
    "Graphs": ["BFS", "DFS", "Topological Sort", "MST/Union-Find", "Dijkstra", "Bellman-Ford", "Floyd-Warshall"],
    "Backtracking": ["Choice-Based", "Constraint-Based", "Grid/Path", "Sequence Generation"],
    "Greedy": ["Intervals & Reach", "Sorting/Local Choice"],
    "Dynamic Programming": ["1D Linear", "2D Grid", "DP on Strings", "DP on Intervals", "DP on Trees", "Knapsack/Subset Sum", "DP on Stocks"],
    "Tries": ["Basic Operations", "Word Break", "Bitwise/XOR"],
    "Bit Manipulation": ["Basic Ops", "Subsets/Bitmask", "Advanced XOR"]
}

def seed_syllabus():
    db = SessionLocal()
    try:
        if db.query(SubPattern).count() == 0:
            for pattern, sub_patterns in SYLLABUS_SKELETON.items():
                for sp_name in sub_patterns:
                    sp = SubPattern(pattern=pattern, name=sp_name)
                    db.add(sp)
            db.commit()
    finally:
        db.close()

seed_syllabus()

# Auto-linker helper
def auto_link_problem(db: Session, problem_id: int, title: str):
    if not title: return
    title_lower = title.strip().lower()
    questions = db.query(SyllabusQuestion).all()
    for q in questions:
        if q.question_title.strip().lower() == title_lower:
            q.linked_problem_id = problem_id
            q.completed = True
            db.commit()

# 2. FastAPI app setup
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Pydantic Models
class ProblemCreate(BaseModel):
    title: Optional[str] = None
    description: str
    difficulty: Optional[str] = None
    leetcode_url: Optional[str] = None

class ProblemSummary(BaseModel):
    id: int
    title: Optional[str] = None
    pattern: Optional[str] = None
    difficulty: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

# 4. Endpoints

def fetch_leetcode_problem(url: str):
    try:
        slug_match = re.search(r'/problems/([^/]+)', url)
        if not slug_match: return None
        slug = slug_match.group(1)
        
        graphql_url = 'https://leetcode.com/graphql'
        json_data = {
            'operationName': 'questionData',
            'variables': {'titleSlug': slug},
            'query': 'query questionData($titleSlug: String!) { question(titleSlug: $titleSlug) { title content difficulty } }'
        }
        headers = {'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'}
        resp = requests.post(graphql_url, json=json_data, headers=headers, timeout=10)
        if resp.status_code == 200:
            data = resp.json().get('data', {}).get('question', {})
            if data and data.get('content'):
                import html
                clean_content = re.sub(r'<[^>]+>', ' ', data['content'])
                clean_content = html.unescape(clean_content)
                data['content'] = clean_content.strip()
                return data
    except Exception as e:
        print(f"Error fetching LeetCode: {e}")
    return None

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/problems")
def create_problem(problem_in: ProblemCreate, db: Session = Depends(get_db)):
    if problem_in.leetcode_url:
        lc_data = fetch_leetcode_problem(problem_in.leetcode_url)
        if lc_data:
            problem_in.title = lc_data.get('title')
            problem_in.description = lc_data.get('content')
            problem_in.difficulty = lc_data.get('difficulty')

    existing_problem = None
    if problem_in.title:
        existing_problem = db.query(Problem).filter(Problem.title == problem_in.title).first()
    
    if not existing_problem and problem_in.description.strip():
        existing_problem = db.query(Problem).filter(Problem.description == problem_in.description).first()
        
    if existing_problem:
        return existing_problem

    if problem_in.title:
        problem_text = f"Title: {problem_in.title}\n\nDescription:\n{problem_in.description}"
    else:
        problem_text = problem_in.description
        
    generated_data = generate_solution(problem_text)
    
    final_title = problem_in.title
    if not final_title and not generated_data.get("error"):
        final_title = generated_data.get("title")
    
    db_problem = Problem(
        title=final_title,
        description=problem_in.description,
        source="manual",
        generated=generated_data,
        pattern=generated_data.get("pattern") if not generated_data.get("error") else None,
        difficulty=problem_in.difficulty
    )
    db.add(db_problem)
    db.commit()
    db.refresh(db_problem)
    
    # Auto-link
    if db_problem.title:
        auto_link_problem(db, db_problem.id, db_problem.title)
        
    return db_problem

@app.get("/problems", response_model=List[ProblemSummary])
def get_problems(db: Session = Depends(get_db)):
    problems = db.query(Problem.id, Problem.title, Problem.pattern, Problem.difficulty, Problem.created_at).all()
    return [
        {
            "id": p.id, 
            "title": p.title, 
            "pattern": p.pattern, 
            "difficulty": p.difficulty,
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

class ProblemNotesUpdate(BaseModel):
    notes: str

@app.put("/problems/{problem_id}/notes")
def update_notes(problem_id: int, notes_in: ProblemNotesUpdate, db: Session = Depends(get_db)):
    problem = db.query(Problem).filter(Problem.id == problem_id).first()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    problem.notes = notes_in.notes
    db.commit()
    return {"status": "updated"}

class ProblemDifficultyUpdate(BaseModel):
    difficulty: Optional[str] = None

@app.patch("/problems/{problem_id}/difficulty")
def update_difficulty(problem_id: int, diff_in: ProblemDifficultyUpdate, db: Session = Depends(get_db)):
    problem = db.query(Problem).filter(Problem.id == problem_id).first()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    problem.difficulty = diff_in.difficulty
    db.commit()
    return {"status": "updated"}

@app.put("/problems/{problem_id}")
def update_and_regenerate(problem_id: int, problem_in: ProblemCreate, db: Session = Depends(get_db)):
    problem = db.query(Problem).filter(Problem.id == problem_id).first()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
        
    problem_text = f"Title: {problem_in.title}\n\nDescription:\n{problem_in.description}" if problem_in.title else problem_in.description
    generated_data = generate_solution(problem_text)
    
    final_title = problem_in.title
    if not final_title and not generated_data.get("error"):
        final_title = generated_data.get("title")
        
    problem.title = final_title
    problem.description = problem_in.description
    problem.generated = generated_data
    problem.pattern = generated_data.get("pattern") if not generated_data.get("error") else problem.pattern
    
    db.commit()
    db.refresh(problem)
    
    if problem.title:
        auto_link_problem(db, problem.id, problem.title)
        
    return problem

@app.post("/problems/backfill-patterns")
def backfill_patterns(db: Session = Depends(get_db)):
    problems = db.query(Problem).filter(Problem.pattern.is_(None)).all()
    count = 0
    for p in problems:
        pattern = None
        if p.generated and isinstance(p.generated, dict) and p.generated.get("pattern"):
            pattern = p.generated.get("pattern")
        else:
            pattern = classify_pattern(p.description)
            
        p.pattern = pattern
        count += 1
        
    db.commit()
    return {"status": "success", "updated": count}

# --- SYLLABUS ENDPOINTS ---
@app.get("/syllabus")
def get_syllabus(db: Session = Depends(get_db)):
    sub_patterns = db.query(SubPattern).all()
    tree = {}
    for sp in sub_patterns:
        if sp.pattern not in tree:
            tree[sp.pattern] = []
        
        questions = []
        for q in sp.questions:
            questions.append({
                "id": q.id,
                "question_title": q.question_title,
                "difficulty": q.difficulty,
                "completed": q.completed,
                "linked_problem_id": q.linked_problem_id
            })
            
        tree[sp.pattern].append({
            "id": sp.id,
            "name": sp.name,
            "description": sp.description,
            "questions": questions
        })
    return tree

@app.post("/syllabus/suggest/{sub_pattern_id}")
def suggest_syllabus_questions(sub_pattern_id: int, db: Session = Depends(get_db)):
    sp = db.query(SubPattern).filter(SubPattern.id == sub_pattern_id).first()
    if not sp: raise HTTPException(status_code=404, detail="Sub-pattern not found")
    
    suggested = suggest_questions(sp.pattern, sp.name)
    added = []
    for q in suggested:
        # Ignore if question already exists
        existing = db.query(SyllabusQuestion).filter(
            SyllabusQuestion.sub_pattern_id == sp.id,
            SyllabusQuestion.question_title.ilike(q.get("question_title", ""))
        ).first()
        if existing: continue
        
        sq = SyllabusQuestion(
            sub_pattern_id=sp.id,
            question_title=q.get("question_title", "Unknown Question"),
            difficulty=q.get("difficulty", "Medium")
        )
        db.add(sq)
        added.append(sq)
    
    db.commit()
    
    # Auto-link newly suggested questions with existing problems
    for q in added:
        prob = db.query(Problem).filter(Problem.title.ilike(q.question_title)).first()
        if prob:
            q.linked_problem_id = prob.id
            q.completed = True
    db.commit()
    
    return {"status": "success", "added": len(added)}

class SyllabusQuestionCreate(BaseModel):
    sub_pattern_id: int
    question_title: str
    difficulty: Optional[str] = "Medium"

@app.post("/syllabus/question")
def add_custom_question(q_in: SyllabusQuestionCreate, db: Session = Depends(get_db)):
    sq = SyllabusQuestion(
        sub_pattern_id=q_in.sub_pattern_id,
        question_title=q_in.question_title,
        difficulty=q_in.difficulty
    )
    db.add(sq)
    db.commit()
    db.refresh(sq)
    
    prob = db.query(Problem).filter(Problem.title.ilike(sq.question_title)).first()
    if prob:
        sq.linked_problem_id = prob.id
        sq.completed = True
        db.commit()
        db.refresh(sq)
    
    return sq

class SyllabusQuestionUpdate(BaseModel):
    completed: Optional[bool] = None
    linked_problem_id: Optional[int] = None

@app.patch("/syllabus/question/{q_id}")
def update_question(q_id: int, q_in: SyllabusQuestionUpdate, db: Session = Depends(get_db)):
    sq = db.query(SyllabusQuestion).filter(SyllabusQuestion.id == q_id).first()
    if not sq: raise HTTPException(status_code=404, detail="Question not found")
    
    if q_in.completed is not None:
        sq.completed = q_in.completed
    if q_in.linked_problem_id is not None:
        sq.linked_problem_id = q_in.linked_problem_id
        
    db.commit()
    return {"status": "success"}

@app.delete("/syllabus/question/{q_id}")
def delete_question(q_id: int, db: Session = Depends(get_db)):
    sq = db.query(SyllabusQuestion).filter(SyllabusQuestion.id == q_id).first()
    if not sq: raise HTTPException(status_code=404, detail="Question not found")
    db.delete(sq)
    db.commit()
    return {"status": "deleted"}
