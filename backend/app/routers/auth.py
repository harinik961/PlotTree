from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.schemas import UserSignup, UserLogin
from app.auth import hash_password, verify_password, create_token
from sqlalchemy import select 


router = APIRouter()

@router.post("/signup")
def signup(user:UserSignup, db: Session = Depends(get_db)):
    correctAnswer = db.query(User).filter(User.email == user.email).first()
    if correctAnswer:
        raise HTTPException(status_code=400, detail="email alr registered try to remember :)")
    else:
        hashed_pass = hash_password(user.password)
        new_user= User(email= user.email, password_hash= hashed_pass) # i dont hace a UserSignup class??
        # Add and commit
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        token = create_token(new_user.id)
        return {"access_token": token, "token_type": "bearer"}

@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    findUser = db.query(User).filter(User.email == user.email).first()
    if not findUser:
        raise HTTPException(status_code= 401, detail="invalid credentials")
    else:
        password_correct = verify_password(user.password, findUser.password_hash)
        if not password_correct:
            raise HTTPException(status_code=401, detail="invalid credentials")
        token = create_token(findUser.id)
        return {"access_token": token, "token_type": "bearer"}

