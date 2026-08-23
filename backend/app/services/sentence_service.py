from sqlalchemy.orm import Session

from app.models import Contribution


def create_sentence(
    db: Session,
    branch_id,
    author_id,
    content: str,
):
    contribution = Contribution(
        branch_id=branch_id,
        author_id=author_id,
        content=content,
    )

    db.add(contribution)
    db.commit()
    db.refresh(contribution)

    return contribution


def get_branch_sentences(db: Session, branch_id):
    return (
        db.query(Contribution)
        .filter(Contribution.branch_id == branch_id)
        .all()
    )