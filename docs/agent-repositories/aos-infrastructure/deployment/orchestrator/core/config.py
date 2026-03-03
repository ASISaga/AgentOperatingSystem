"""Deployment configuration models.

Pydantic models that capture every tuneable knob for an AOS infrastructure
lifecycle operation.  The ``DeploymentConfig.from_args()`` factory builds a
config from an argparse ``Namespace``, making it easy to bridge the CLI layer
with the core orchestration engine.

Three-pillar lifecycle settings are grouped under optional sub-configs:
- ``GovernanceConfig`` — policy, cost, and RBAC settings
- ``AutomationConfig`` — pipeline and infrastructure lifecycle settings
- ``ReliabilityConfig`` — drift detection and health monitoring settings
"""

from __future__ import annotations

import argparse
from typing import Literal

from pydantic import BaseModel, Field, model_validator


class GovernanceConfig(BaseModel):
    """Governance pillar configuration."""

    enforce_policies: bool = False
    """Assign and evaluate AOS governance policies on every deployment."""

    budget_amount: float = 0.0
    """Monthly budget limit in the subscription currency (0 = disabled)."""

    budget_alert_emails: list[str] = Field(default_factory=list)
    """Email addresses to notify when a budget threshold is crossed."""

    required_tags: dict[str, str] = Field(default_factory=dict)
    """Tag key→value pairs that every resource must carry."""

    allowed_locations: list[str] = Field(default_factory=list)
    """Locations allowed by the Allowed Locations policy (empty = all)."""

    review_rbac: bool = False
    """Run a privileged-access review after deployment."""


class AutomationConfig(BaseModel):
    """Automation pillar configuration."""

    deploy_function_apps: bool = False
    """After Bicep provisioning, deploy AOS Function Apps via the SDK bridge."""

    app_names: list[str] = Field(default_factory=list)
    """Specific app names to deploy (empty = all canonical AOS apps)."""

    sync_kernel_config: bool = False
    """After deployment, sync KernelConfig env vars to all Function Apps."""

    enable_lifecycle_ops: bool = False
    """Expose lifecycle operations (deprovision/shift/modify/upgrade/scale)."""

    target_version: str = ""
    """Infrastructure version tag used for upgrade tracking."""

    scale_overrides: dict[str, str] = Field(default_factory=dict)
    """Mapping of ``resource_name → target_SKU`` for upgrade/scale operations."""

    region_shift_target: str = ""
    """Target region for a shift operation (empty = disabled)."""


class ReliabilityConfig(BaseModel):
    """Reliability pillar configuration."""

    enable_drift_detection: bool = False
    """Run a drift-detection scan after deployment."""

    drift_manifest: list[dict] = Field(default_factory=list)
    """Optional explicit resource manifest to compare against live state.
    When empty the Bicep what-if output is used instead."""

    sla_target: float | None = None
    """Override the default SLA target percentage for SLA compliance checks."""

    check_dr_readiness: bool = False
    """Assess disaster-recovery readiness (KV soft-delete, geo-replication)."""


class DeploymentConfig(BaseModel):
    """Configuration for an AOS infrastructure lifecycle operation."""

    environment: Literal["dev", "staging", "prod"]
    resource_group: str = Field(min_length=1)
    location: str = Field(min_length=1)
    location_ml: str = ""
    template: str = ""
    parameters_file: str = ""
    subscription_id: str = ""
    git_sha: str = ""
    allow_warnings: bool = False
    skip_health: bool = False
    dry_run: bool = False

    # --- Three-pillar lifecycle extensions ---
    governance: GovernanceConfig = Field(default_factory=GovernanceConfig)
    automation: AutomationConfig = Field(default_factory=AutomationConfig)
    reliability: ReliabilityConfig = Field(default_factory=ReliabilityConfig)

    @model_validator(mode="after")
    def _set_defaults(self) -> "DeploymentConfig":
        """Derive sensible defaults for optional fields."""
        if not self.location_ml:
            self.location_ml = self.location
        if not self.resource_group:
            self.resource_group = f"rg-aos-{self.environment}"
        return self

    @classmethod
    def from_args(cls, args: argparse.Namespace) -> "DeploymentConfig":
        """Build a config from an argparse Namespace."""
        governance = GovernanceConfig(
            enforce_policies=getattr(args, "enforce_policies", False),
            budget_amount=float(getattr(args, "budget_amount", 0) or 0),
            required_tags=getattr(args, "required_tags", {}),
            review_rbac=getattr(args, "review_rbac", False),
        )
        automation = AutomationConfig(
            deploy_function_apps=getattr(args, "deploy_function_apps", False),
            sync_kernel_config=getattr(args, "sync_kernel_config", False),
            enable_lifecycle_ops=getattr(args, "enable_lifecycle_ops", False),
            region_shift_target=getattr(args, "region_shift_target", ""),
        )
        reliability = ReliabilityConfig(
            enable_drift_detection=getattr(args, "enable_drift_detection", False),
            check_dr_readiness=getattr(args, "check_dr_readiness", False),
        )
        return cls(
            environment=args.environment,
            resource_group=args.resource_group,
            location=args.location,
            location_ml=getattr(args, "location_ml", ""),
            template=getattr(args, "template", ""),
            parameters_file=getattr(args, "parameters", ""),
            subscription_id=getattr(args, "subscription_id", ""),
            git_sha=getattr(args, "git_sha", ""),
            allow_warnings=getattr(args, "allow_warnings", False),
            skip_health=getattr(args, "skip_health", False),
            dry_run=getattr(args, "no_confirm_deletes", False),
            governance=governance,
            automation=automation,
            reliability=reliability,
        )
