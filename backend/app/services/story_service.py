from typing import Annotated
from uuid import UUID
from sqlalchemy.orm import Session
from app.dependencies import db_dependency
from app.models import Story, Branch

# a service folder is where all hte business logic is stored, so like helpers? StoryCreate is the infromation i will get from the post method ig? 
def create_story(db: Session, owner_id, title:str, is_public: bool):
     story = Story(owner_id=owner_id, title = title, is_public = is_public)
     db.add(story)
     db.commit()
     db.refresh(story)
     return story

def get_all_stories(db:Session):
     return db.query(Story).all()
def get_story_by_id(db: Session, id):
     return db.query(Story).filter(Story.id == id).first()
def create_branch(db:Session, owner_id: UUID, story_id: UUID, title: str, parent_branch: UUID):
     if parent_branch:

        parent_branch_name = (
            db.query(Branch)
            .filter(Branch.id == parent_branch)
            .first()
        )
        if parent_branch_name is None:
            raise HTTPException(
                status_code=404,
                detail="Parent branch not found"
            )

        if parent_branch_name.story_id != story_id:
            raise HTTPException(
                status_code=400,
                detail="Parent branch belongs to different story"
            )

     branch = Branch(story_id=story_id,owner_id=owner_id,title=title,parent_branch=parent_branch)

     db.add(branch)
     db.commit()
     db.refresh(branch)
     return branch
def get_story_branches(db: Session, story_id: UUID):
    return db.query(Branches).filter(Branches.story_id == story_id).all()
