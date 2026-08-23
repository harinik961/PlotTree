# a post method is a method that is used to create a new resource. In this case, 
# we are creating a new story. The post method will take in the story data 
# and create a new story in the database.
from typing import Annotated

from app.services.story_service import get_all_stories, create_story, get_story_by_id, create_branch
from app.dependencies import get_current_user, db_dependency
from fastapi import APIRouter, Depends
from app.schemas import StoryCreate
from app.models import User
from app.services.story_service import create_story, get_story_by_id
from uuid import UUID
from app.schemas import BranchCreate
from app.services.story_service import create_branch
from fastapi import HTTPException

user_dependency = Annotated[User, Depends(get_current_user)]


router = APIRouter()

@router.post("/stories")
# storyCreate gives name of title and whether public or not 
def create_new_story(story_data: StoryCreate, curr_user: user_dependency, db: db_dependency):
    return create_story(db=db, owner_id=curr_user.id, title=story_data.title, is_public=story_data.is_public)

@router.get("/stories/{id}")
def get_by_id(db: db_dependency, id):
    return get_story_by_id(db, id)

@router.get("/stories")
def get_all(db: db_dependency):
    return get_all_stories(db)

@router.post("/stories/{story_id}/branches")
def create_new_branch(
    story_id: UUID,
    branch_data: BranchCreate,
    curr_user: user_dependency,
    db: db_dependency
):

    story = get_story_by_id(db, story_id)

    if story is None:
        raise HTTPException(
            status_code=404,
            detail="Story not found"
        )

    return create_branch(
        db=db,
        story_id=story_id,
        owner_id=curr_user.id,
        title=branch_data.title,
        parent_branch_id=branch_data.parent_branch_id
    )

@router.get("/stories/{story_id}/branches")
def get_branches(story_id: UUID, db: db_dependency):
    return story_service.get_story_branches(db, story_id)