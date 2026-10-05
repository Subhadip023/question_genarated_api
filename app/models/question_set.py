from sqlalchemy import Column, ForeignKey, Index, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.database import Base

class QuestionSet(Base):
    __tablename__ = "question_sets"
    __table_args__ = (
        Index("ix_fk_question_sets_org_id", "org_id"),
        Index("ix_fk_question_sets_user_id", "user_id"),
    )

    id = Column(Integer, primary_key=True)

    name = Column(String(255), nullable=False)

    org_id = Column(Integer, ForeignKey("organizations.id"))

    user_id = Column(Integer, ForeignKey("users.id"))

    is_active = Column(Boolean, default=True)

    visibility = Column(Integer, default=0)

    questions = relationship(
        "QuestionSetQuestion",
        cascade="all, delete"
    )