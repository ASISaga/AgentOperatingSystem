"""Data models for the AOS Client SDK."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class AgentDescriptor(BaseModel):
    """Describes an agent available in the RealmOfAgents catalog."""

    agent_id: str = Field(..., description="Unique agent identifier")
    agent_type: str = Field(..., description="Agent class name (e.g. LeadershipAgent, CMOAgent)")
    purpose: str = Field(..., description="The agent's long-term purpose")
    adapter_name: str = Field(..., description="LoRA adapter providing domain expertise")
    capabilities: List[str] = Field(default_factory=list, description="Agent capabilities")
    config: Dict[str, Any] = Field(default_factory=dict, description="Agent-specific configuration")


class OrchestrationPurpose(BaseModel):
    """The overarching purpose that drives an orchestration.

    When set on an :class:`OrchestrationRequest`, participating
    :class:`PurposeDrivenAgent` instances align their working purposes to
    achieve this overarching goal while retaining their own domain-specific
    knowledge, skills, and personas.
    """

    purpose: str = Field(..., description="The overarching purpose of the orchestration")
    purpose_scope: str = Field(
        default="General orchestration scope",
        description="Boundaries/scope for the orchestration purpose",
    )
    success_criteria: List[str] = Field(
        default_factory=list,
        description="Criteria that define successful orchestration completion",
    )


class OrchestrationRequest(BaseModel):
    """Request to run an agent orchestration via AOS."""

    orchestration_id: Optional[str] = Field(None, description="Client-supplied ID (auto-generated if omitted)")
    agent_ids: List[str] = Field(..., min_length=1, description="Agent IDs to include in the orchestration")
    workflow: str = Field(default="collaborative", description="Workflow pattern: collaborative, sequential, hierarchical")
    purpose: Optional[OrchestrationPurpose] = Field(None, description="Overarching purpose that drives the orchestration and guides agent alignment")
    task: Dict[str, Any] = Field(..., description="Task payload for the orchestration")
    config: Dict[str, Any] = Field(default_factory=dict, description="Orchestration-level configuration")
    callback_url: Optional[str] = Field(None, description="Webhook URL for completion notification")


class OrchestrationStatusEnum(str, Enum):
    """Orchestration lifecycle states."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class OrchestrationStatus(BaseModel):
    """Status of a submitted orchestration."""

    orchestration_id: str
    status: OrchestrationStatusEnum
    agent_ids: List[str] = Field(default_factory=list)
    progress: float = Field(default=0.0, ge=0.0, le=1.0, description="Progress 0.0-1.0")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    error: Optional[str] = None


class OrchestrationResult(BaseModel):
    """Final result of a completed orchestration."""

    orchestration_id: str
    status: OrchestrationStatusEnum
    agent_ids: List[str] = Field(default_factory=list)
    results: Dict[str, Any] = Field(default_factory=dict, description="Per-agent results keyed by agent_id")
    summary: Optional[str] = Field(None, description="Aggregated summary of the orchestration outcome")
    created_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None
