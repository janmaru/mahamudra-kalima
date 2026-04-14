"""Kalima package initialization."""

__version__ = "0.1.0"

from .types import Message, Session, TaskCategory
from .classifier import TaskClassifier, classify_message, classify_messages

__all__ = [
    "Message",
    "Session",
    "TaskCategory",
    "TaskClassifier",
    "classify_message",
    "classify_messages",
]
