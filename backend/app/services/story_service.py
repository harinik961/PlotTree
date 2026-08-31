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
def create_branch(db:Session, owner_id: UUID, story_id: UUID, title: str, parent_branch: UUID|None):
    fork_sentence_id = None
    if parent_branch_id:
        last_sentence = (
            db.query(Sentences)
            .filter(Sentences.branch_id == parent_branch_id)
            .order_by(Sentences.created_at.desc())
            .first()
        )
        if last_sentence:
            fork_sentence_id = last_sentence.id

    branch = Branches(
        id=uuid.uuid4(),
        story_id=story_id,
        title=title,
        parent_branch=parent_branch_id,
        fork_sentence_id=fork_sentence_id,
    )
    db.add(branch)
    db.commit()
    db.refresh(branch)
    return branch
def get_story_branches(db: Session, story_id: UUID):
    return db.query(Branches).filter(Branches.story_id == story_id).all()

# new function to retrieve the full story for a given branch  
def get_full_story(db: Session, branch_id: UUID):
    chain = []
    current = db.query(Branches).filter(Branches.id == branch_id).first()

    while current:
        sentences = (
            db.query(Sentences)
            .filter(Sentences.branch_id == current.id)
            .order_by(Sentences.created_at)
            .all()
        )

        if current.id != branch_id and current.fork_sentence_id:
            # for ancestor branches, cut off at the fork point
            fork_sentence = db.query(Sentences).get(current.fork_sentence_id)
            sentences = [s for s in sentences if s.created_at <= fork_sentence.created_at]

        chain.append({
            "branch_id": str(current.id),
            "branch_title": current.title,
            "sentences": [
                {"id": str(s.id), "content": s.content, "author_id": str(s.author_id)}
                for s in sentences
            ]
        })

        current = (
            db.query(Branches).filter(Branches.id == current.parent_branch).first()
            if current.parent_branch else None
        )

    chain.reverse()
    return chain

def create_sentence(db: Session, branch_id: UUID, author_id: UUID, content: str):
    sentence = Sentences(
        id=uuid.uuid4(),
        branch_id=branch_id,
        author_id=author_id,
        content=content,
        created_at=datetime.utcnow(),
    )
    db.add(sentence)
    db.commit()
    db.refresh(sentence)
    return sentence