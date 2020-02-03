"""Representation GitHub file."""
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from airflow_utils.models.base import Base


class File(Base):
    """Representation GitHub file."""

    __tablename__ = "file"

    sha = Column(String, primary_key=True)
    filename = Column(String, nullable=False)
    pull_requests = relationship("AssociationPullRequestFile", back_populates="file")
