from uuid import UUID
from typing import Optional
from pydantic import BaseModel, EmailStr
# this is all related to what the html methods get
class UserSignup(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
class StoryCreate(BaseModel):
    title: str
    is_public: bool = False
class BranchCreate(BaseModel):
    title: str
    parent_branch_id: UUID | None = None
class SentenceCreate(BaseModel):
    content: str