"""Shared schema definitions."""
from datetime import datetime

from pydantic import BaseModel


class TimeStampedModel(BaseModel):
    """Base schema that exposes creation timestamps."""

    as_of: datetime

    class Config:
        from_attributes = True


class Message(BaseModel):
    """A simple message envelope."""

    message: str