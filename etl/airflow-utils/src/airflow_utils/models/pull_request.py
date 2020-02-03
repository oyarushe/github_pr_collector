"""Representation GitHub Pull Request."""
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from airflow_utils.models.base import Base


class PullRequest(Base):
    """Representation GitHub Pull Request."""

    __tablename__ = "pull_request"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    merged = Column(Boolean, nullable=False)
    created_at = Column(DateTime, nullable=False)
    closed_at = Column(DateTime, nullable=False)
    repo_id = Column(Integer, ForeignKey('repo.id', ondelete='CASCADE'))
    repo = relationship("Repo", back_populates="pull_requests")
    files = relationship("AssociationPullRequestFile", back_populates="pull_request")
