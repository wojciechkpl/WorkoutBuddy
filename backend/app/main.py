from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from . import models, schemas, crud, database, ml
from passlib.context import CryptContext

app = FastAPI()

models.Base.metadata.create_all(bind=database.engine)


# Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def read_root():
    return {"message": "Welcome to WorkoutBuddy API!"}


@app.post("/register", response_model=schemas.User)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)


@app.post("/goals", response_model=schemas.Goal)
def create_goal(goal: schemas.GoalCreate, user_id: int, db: Session = Depends(get_db)):
    # In production, get user_id from JWT token
    return crud.create_goal(db=db, goal=goal, user_id=user_id)


@app.post("/ml/personalized-plan")
def personalized_plan(user_id: int, db: Session = Depends(get_db)):
    # In production, fetch user data and pass to ML model
    user = crud.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return ml.generate_personalized_plan({"user_id": user_id})


# Routers for users, goals, ML, etc. will be included here as the app grows.
