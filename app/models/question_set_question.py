from sqlalchemy import Column, ForeignKey, Index, Integer
from sqlalchemy.orm import relationship
from app.database import Base

class QuestionSetQuestion(Base):
    __tablename__ = "question_set_questions"
    __table_args__ = (
        Index("ix_fk_question_set_questions_set_id", "set_id"),
        Index("ix_fk_question_set_questions_question_id", "question_id"),
    )

    id = Column(Integer, primary_key=True)

    set_id = Column(Integer, ForeignKey("question_sets.id"))

    question_id = Column(Integer, ForeignKey("questions.id"))