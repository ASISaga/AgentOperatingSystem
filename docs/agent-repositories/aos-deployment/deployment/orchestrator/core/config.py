"""Deployment configuration models.

Pydantic models that capture every tuneable knob for an AOS infrastructure
deployment.  The ``DeploymentConfig.from_args()`` factory builds a config
from an argparse ``Namespace``, making it easy to bridge the CLI layer with
the core orchestration engine.
"""

from __future__ import annotations

import argparse
from typing import Literal

from pydantic import BaseModel, Field, model_validator


class DeploymentConfig(BaseModel):
    """Configuration for an AOS infrastructure deployment."""

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
        )
