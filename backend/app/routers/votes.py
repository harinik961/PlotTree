from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.dependencies import get_current_user
from app.models import User

from app.services.vote_service import (
    cast_vote,
    get_vote_count,
)

router = APIRouter(prefix="/votes", tags=["votes"])

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[User, Depends(get_current_user)]


@router.post("/{branch_id}/vote")
def create_vote(
    branch_id,
    curr_user: user_dependency,
    db: db_dependency,
):
    return cast_vote(
        db=db,
        branch_id=branch_id,
        author_id=curr_user.id,
    )


@router.get("/{branch_id}/votes")
def get_votes(
    branch_id,
    db: db_dependency,
):
    count = get_vote_count(
        db=db,
        branch_id=branch_id,
    )

    return {"votes": count}