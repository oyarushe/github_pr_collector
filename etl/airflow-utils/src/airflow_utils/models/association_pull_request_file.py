"""Association table for Pull Request and File."""
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from airflow_utils.models.base import Base


class AssociationPullRequestFile(Base):
    """Association table for Pull Request and File."""

    __tablename__ = "association_pull_request_file"

    pull_request_id = Column(Integer, ForeignKey("pull_request.id", ondelete='CASCADE'), primary_key=True)
    file_sha = Column(String, ForeignKey("file.sha", ondelete='CASCADE'), primary_key=True)
    pull_request = relationship("PullRequest", back_populates="files")
    file = relationship("File", back_populates="pull_requests")
