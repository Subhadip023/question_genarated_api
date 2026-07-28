from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class QuestionSetQuestion(Base):
    __tablename__ = "question_set_questions"

    id = Column(Integer, primary_key=True)

    set_id = Column(Integer, ForeignKey("question_sets.id"))

    question_id = Column(Integer, ForeignKey("questions.id"))