"""Data models for Kalima using Pydantic."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class TaskCategory(str, Enum):
    """13 task categories for classification."""

    CODING = "Coding"
    DEBUGGING = "Debugging"
    FEATURE_DEV = "Feature Dev"
    REFACTORING = "Refactoring"
    TESTING = "Testing"
    EXPLORATION = "Exploration"
    PLANNING = "Planning"
    DELEGATION = "Delegation"
    GIT_OPS = "Git Ops"
    BUILD_DEPLOY = "Build/Deploy"
    BRAINSTORMING = "Brainstorming"
    CONVERSATION = "Conversation"
    GENERAL = "General"


class Message(BaseModel):
    """A single message in a Claude Code session."""

    model_config = ConfigDict(use_enum_values=False)

    api_message_id: str
    timestamp: datetime
    model: str
    input_tokens: int = 0
    output_tokens: int = 0
    cache_write_tokens: int = 0
    cache_read_tokens: int = 0
    tool_uses: list[str] = Field(default_factory=list)
    user_text: str = ""
    task_category: TaskCategory = TaskCategory.GENERAL
    cost_usd: float = 0.0


class Session(BaseModel):
    """A Claude Code session with multiple messages."""

    model_config = ConfigDict(use_enum_values=False)

    session_id: str
    project_name: str
    created_at: datetime
    updated_at: datetime
    messages: list[Message] = Field(default_factory=list)

    @property
    def total_tokens(self) -> int:
        """Total input + output tokens (excludes cache)."""
        return sum(m.input_tokens + m.output_tokens for m in self.messages)

    @property
    def total_cost_usd(self) -> float:
        """Total cost across all messages in USD."""
        return sum(m.cost_usd for m in self.messages)

    @property
    def total_input_tokens(self) -> int:
        return sum(m.input_tokens for m in self.messages)

    @property
    def total_output_tokens(self) -> int:
        return sum(m.output_tokens for m in self.messages)

    @property
    def total_cache_write_tokens(self) -> int:
        return sum(m.cache_write_tokens for m in self.messages)

    @property
    def total_cache_read_tokens(self) -> int:
        return sum(m.cache_read_tokens for m in self.messages)


class DailyCost(BaseModel):
    """Daily cost summary."""

    date: str  # YYYY-MM-DD
    cost_usd: float
    input_tokens: int
    output_tokens: int
    cache_write_tokens: int
    cache_read_tokens: int
    message_count: int


class PeriodSummary(BaseModel):
    """Summary for a date range."""

    start_date: datetime
    end_date: datetime
    total_cost_usd: float
    total_input_tokens: int
    total_output_tokens: int
    total_cache_write_tokens: int
    total_cache_read_tokens: int
    daily_costs: list[DailyCost] = Field(default_factory=list)
    by_model: dict[str, float] = Field(default_factory=dict)
    by_category: dict[str, float] = Field(default_factory=dict)
    message_count: int = 0


@dataclass
class ModelPricing:
    """Pricing for a Claude model."""

    name: str
    input_cost_per_mtok: float  # cost per 1M input tokens
    output_cost_per_mtok: float  # cost per 1M output tokens
    cache_write_cost_per_mtok: float = 0.0
    cache_read_cost_per_mtok: float = 0.0

    def calculate_cost(
        self,
        input_tokens: int,
        output_tokens: int,
        cache_write_tokens: int = 0,
        cache_read_tokens: int = 0,
    ) -> float:
        """Calculate total cost for this model."""
        input_cost = (input_tokens / 1_000_000) * self.input_cost_per_mtok
        output_cost = (output_tokens / 1_000_000) * self.output_cost_per_mtok
        cache_write_cost = (
            (cache_write_tokens / 1_000_000) * self.cache_write_cost_per_mtok
        )
        cache_read_cost = (cache_read_tokens / 1_000_000) * self.cache_read_cost_per_mtok
        return input_cost + output_cost + cache_write_cost + cache_read_cost
