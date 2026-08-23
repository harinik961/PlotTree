from sqlalchemy.orm import Session

from app.models import Vote
from fastapi import HTTPException

def cast_vote(
    db: Session,
    branch_id,
    author_id,
):
    existing = db.query(Vote).filter(
        Vote.branch_id == branch_id,
        Vote.author_id == author_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="already voted on this branch")
    vote = Vote(
        branch_id=branch_id,
        author_id=author_id,
    )

    db.add(vote)
    db.commit()
    db.refresh(vote)

    return vote


def get_vote_count(
    db: Session,
    branch_id,
):
    return (
        db.query(Vote)
        .filter(Vote.branch_id == branch_id)
        .count()
    )