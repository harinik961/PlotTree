from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    stories = relationship("Story", back_populates="owner")

class Story(Base):
    __tablename__ = "stories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    is_public = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="stories")

class Contribution(Base):
    __tablename__ = "sentences"
    version = Column(Integer, default=1)
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    branch_id = Column(UUID(as_uuid = True), ForeignKey("branches.id"), nullable=False)
    author_id = Column(UUID(as_uuid = True), ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime,  default=datetime.utcnow )
class Branch(Base):
    __tablename__ = "branches"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    story_id = Column(UUID(as_uuid = True), ForeignKey("stories.id"), nullable=False)
    parent_branch = Column(UUID(as_uuid = True), ForeignKey("branches.id"), nullable=True) #need to fix 
    title = Column(String, nullable=False)
    winner = Column(Boolean, nullable=True)
    voting_ends_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime,  default=datetime.utcnow )
    owner_id = Column(UUID(as_uuid = True), ForeignKey("users.id"), nullable = False)
class Vote(Base):
    __tablename__= "votes"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    branch_id = Column(UUID(as_uuid = True), ForeignKey("branches.id"), nullable=False)
    author_id = Column(UUID(as_uuid = True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime,  default=datetime.utcnow )
class Event(Base):
    __tablename__ = "events"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sentence_id = Column(UUID(as_uuid=True), ForeignKey("sentences.id"), nullable=False)
    content_snapshot = Column(Text, nullable=False)
    version = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)



