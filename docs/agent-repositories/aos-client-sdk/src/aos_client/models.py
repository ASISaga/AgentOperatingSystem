"""Data models for the AOS Client SDK.

All orchestration models follow the **purpose-driven, perpetual** paradigm:
orchestrations are started with a purpose and run indefinitely until
explicitly stopped.  There are no completion criteria or finite task
payloads — agents work toward the overarching purpose continuously.
"""

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

    Purposes are **perpetual** — they have no success criteria because a
    purpose-driven orchestration runs indefinitely.
    """

    purpose: str = Field(..., description="The overarching purpose of the orchestration")
    purpose_scope: str = Field(
        default="General orchestration scope",
        description="Boundaries/scope for the orchestration purpose",
    )


class OrchestrationRequest(BaseModel):
    """Request to start a purpose-driven agent orchestration via AOS.

    Orchestrations are perpetual: they run until explicitly stopped.
    The ``purpose`` drives agent alignment; ``context`` supplies initial
    data that informs the agents' work.
    """

    orchestration_id: Optional[str] = Field(None, description="Client-supplied ID (auto-generated if omitted)")
    agent_ids: List[str] = Field(..., min_length=1, description="Agent IDs to include in the orchestration")
    workflow: str = Field(default="collaborative", description="Workflow pattern: collaborative, sequential, hierarchical")
    purpose: OrchestrationPurpose = Field(..., description="Overarching purpose that drives the orchestration and guides agent alignment")
    context: Dict[str, Any] = Field(default_factory=dict, description="Initial context data for the orchestration")
    config: Dict[str, Any] = Field(default_factory=dict, description="Orchestration-level configuration")
    callback_url: Optional[str] = Field(None, description="Webhook URL for status notifications")


class OrchestrationStatusEnum(str, Enum):
    """Orchestration lifecycle states.

    Orchestrations are perpetual — they transition from ``PENDING`` to
    ``ACTIVE`` and remain active until explicitly ``STOPPED`` or
    ``CANCELLED``, or until a ``FAILED`` state is reached.
    """

    PENDING = "pending"
    ACTIVE = "active"
    STOPPED = "stopped"
    FAILED = "failed"
    CANCELLED = "cancelled"


class OrchestrationStatus(BaseModel):
    """Status of a submitted orchestration."""

    orchestration_id: str
    status: OrchestrationStatusEnum
    agent_ids: List[str] = Field(default_factory=list)
    purpose: Optional[str] = Field(None, description="The orchestration's driving purpose")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    error: Optional[str] = None
