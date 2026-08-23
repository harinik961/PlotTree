from typing import Annotated, TypeAlias

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.auth import decode_token
from app.database import get_db
from app.models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
db_dependency = Annotated[Session, Depends(get_db)]

def get_current_user(db:db_dependency, token: str = Depends(oauth2_scheme)):
    # decode the token to get user_id 
    try:
        user_id = decode_token(token)
    except:
        raise HTTPException(status_code = 401, detail="invalid token sucks for u")
    # query db for that user 
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code = 401, detail="doesnt exist boohoo")
    # if not found raise 401 
    # return user
    return user
