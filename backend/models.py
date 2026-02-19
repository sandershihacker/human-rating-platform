from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


SESSION_DURATION_MINUTES = 60  # Hard-coded 1 hour per rater


class Experiment(Base):
    __tablename__ = "experiments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    num_ratings_per_question = Column(Integer, default=3)
    prolific_completion_url = Column(String, nullable=True)

    questions = relationship("Question", back_populates="experiment")
    raters = relationship("Rater", back_populates="experiment")


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    experiment_id = Column(Integer, ForeignKey("experiments.id"), nullable=False)
    question_id = Column(String, nullable=False)
    question_text = Column(Text, nullable=False)
    gt_answer = Column(Text, nullable=True)
    options = Column(Text, nullable=True)
    question_type = Column(String, default="MC")
    extra_data = Column(Text, nullable=True)

    experiment = relationship("Experiment", back_populates="questions")
    ratings = relationship("Rating", back_populates="question")


class Rater(Base):
    __tablename__ = "raters"

    id = Column(Integer, primary_key=True, index=True)
    prolific_id = Column(String, nullable=False)
    study_id = Column(String, nullable=True)  # Prolific STUDY_ID
    session_id = Column(String, nullable=True)  # Prolific SESSION_ID
    experiment_id = Column(Integer, ForeignKey("experiments.id"), nullable=False)
    session_start = Column(DateTime, default=datetime.utcnow)
    session_end = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)

    experiment = relationship("Experiment", back_populates="raters")
    ratings = relationship("Rating", back_populates="rater")


class Rating(Base):
    __tablename__ = "ratings"

    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    rater_id = Column(Integer, ForeignKey("raters.id"), nullable=False)
    answer = Column(Text, nullable=False)
    confidence = Column(Integer, nullable=False)
    time_started = Column(DateTime, nullable=False)
    time_submitted = Column(DateTime, default=datetime.utcnow)

    question = relationship("Question", back_populates="ratings")
    rater = relationship("Rater", back_populates="ratings")


class Upload(Base):
    __tablename__ = "uploads"

    id = Column(Integer, primary_key=True, index=True)
    experiment_id = Column(Integer, ForeignKey("experiments.id"), nullable=False)
    filename = Column(String, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    question_count = Column(Integer, nullable=False)

    experiment = relationship("Experiment")
