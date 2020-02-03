"""Representation GitHub Repository."""
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from airflow_utils.models.base import Base


class Repo(Base):
    """Representation GitHub Repository."""

    __tablename__ = "repo"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    pull_requests = relationship("PullRequest", back_populates="repo")
