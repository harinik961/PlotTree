from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.dependencies import get_current_user
from app.models import User
from app.schemas import SentenceCreate
from app.services.sentence_service import (
    create_sentence,
    get_branch_sentences,
)

router = APIRouter(
    prefix="/branches",
    tags=["branches"]
)
db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[User, Depends(get_current_user)]


@router.post("/{branch_id}/sentences")
def add_sentence(
    branch_id,
    sentence_data: SentenceCreate,
    curr_user: user_dependency,
    db: db_dependency,
):
    return create_sentence(
        db=db,
        branch_id=branch_id,
        author_id=curr_user.id,
        content=sentence_data.content,
    )


@router.get("/{branch_id}/sentences")
def get_sentences(
    branch_id,
    db: db_dependency,
):
    return get_branch_sentences(
        db=db,
        branch_id=branch_id,
    )
@router.get("/sentences/{branch_id}/full-story")
def full_story(branch_id: UUID, db: db_dependency):
    return story_service.get_full_story(db, branch_id)