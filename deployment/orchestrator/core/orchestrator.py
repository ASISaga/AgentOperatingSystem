"""
Bicep Orchestrator

Main orchestration class that coordinates the entire deployment lifecycle.
"""

import subprocess
import json
from typing import Dict, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime

from .state_machine import DeploymentState, DeploymentStateMachine
from .failure_classifier import FailureClassifier, FailureType
from ..validators.linter import BicepLinter, LintResult
from ..validators.whatif_planner import WhatIfPlanner, WhatIfResult
from ..health.health_checker import HealthVerifier, AzureResourceHealthChecker, HealthCheckResult
from ..audit.audit_logger import AuditLogger, AuditRecord


class DeploymentConfig:
    """Configuration for a deployment."""
    
    def __init__(self, resource_group: str, location: str, template_file: Path,
                 parameters_file: Optional[Path] = None, allow_warnings: bool = True,
                 require_confirmation_for_deletes: bool = True,
                 skip_health_checks: bool = False, audit_dir: Optional[Path] = None):
        """
        Initialize deployment configuration.
        
        Args:
            resource_group: Target resource group
            location: Azure region
            template_file: Path to Bicep template
            parameters_file: Optional parameters file (.bicepparam or .json)
            allow_warnings: Allow linter warnings
            require_confirmation_for_deletes: Require manual confirmation for destructive changes
            skip_health_checks: Skip post-deployment health verification
            audit_dir: Directory for audit logs (default: ./audit)
        """
        self.resource_group = resource_group
        self.location = location
        self.template_file = template_file
        self.parameters_file = parameters_file
        self.allow_warnings = allow_warnings
        self.require_confirmation_for_deletes = require_confirmation_for_deletes
        self.skip_health_checks = skip_health_checks
        self.audit_dir = audit_dir or Path("./audit")
        self.parameter_overrides: Dict[str, Any] = {}
    
    def add_parameter_override(self, name: str, value: Any):
        """Add a parameter override."""
        self.parameter_overrides[name] = value


class BicepOrchestrator:
    """
    Main orchestrator for Bicep deployments.
    
    Implements the complete deployment lifecycle with quality gates and safety checks.
    """
    
    def __init__(self, config: DeploymentConfig, git_sha: Optional[str] = None):
        """
        Initialize orchestrator.
        
        Args:
            config: Deployment configuration
            git_sha: Git commit SHA for audit trail
        """
        self.config = config
        self.git_sha = git_sha
        self.state_machine = DeploymentStateMachine()
        self.failure_classifier = FailureClassifier()
        self.linter = BicepLinter(allow_warnings=config.allow_warnings)
        self.planner = WhatIfPlanner()
        self.health_verifier = HealthVerifier()
        self.audit_logger = AuditLogger(config.audit_dir)
        self.audit_record: Optional[AuditRecord] = None
        self.last_deploy_error: str = ""
    
    def deploy(self) -> Tuple[bool, str]:
        """
        Execute the full deployment lifecycle.
        
        Returns:
            Tuple of (success, message)
        """
        # Create audit record
        self.audit_record = self.audit_logger.create_record(
            git_sha=self.git_sha,
            template_file=str(self.config.template_file),
            parameters_file=str(self.config.parameters_file) if self.config.parameters_file else None
        )
        
        try:
            # Phase 1: Validate parameters
            if not self._validate_parameters():
                return False, "Parameter validation failed"
            
            # Phase 2: Lint
            if not self._lint_template():
                return False, "Linting failed"
            
            # Phase 3: What-if planning
            if not self._plan_deployment():
                return False, "Planning failed"
            
            # Phase 4: Deploy
            if not self._execute_deployment():
                # Truncate to avoid overly long failure messages in CI output
                max_error_len = 500
                error_detail = self.last_deploy_error[:max_error_len] if self.last_deploy_error else "No error details"
                return False, f"Deployment failed: {error_detail}"
            
            # Phase 5: Verify health
            if not self.config.skip_health_checks:
                if not self._verify_health():
                    return False, "Health verification failed"
            
            # Mark as completed
            self.state_machine.transition_to(DeploymentState.COMPLETED)
            self.audit_record.set_result(True, "Deployment completed successfully")
            self.audit_logger.save_record(self.audit_record)
            
            return True, "Deployment completed successfully"
        
        except Exception as e:
            self.state_machine.transition_to(DeploymentState.FAILED)
            if self.audit_record:
                self.audit_record.set_result(False, f"Deployment failed: {str(e)}")
                self.audit_logger.save_record(self.audit_record)
            return False, f"Deployment failed: {str(e)}"
    
    def _validate_parameters(self) -> bool:
        """Validate deployment parameters."""
        self.state_machine.transition_to(DeploymentState.VALIDATING_PARAMETERS)
        self.audit_record.add_event("validate", "Validating parameters")
        
        # Check template file exists
        if not self.config.template_file.exists():
            self.audit_record.add_event("validate", f"Template file not found: {self.config.template_file}")
            self.state_machine.transition_to(DeploymentState.FAILED)
            return False
        
        # Check parameters file exists if specified
        if self.config.parameters_file and not self.config.parameters_file.exists():
            self.audit_record.add_event("validate", f"Parameters file not found: {self.config.parameters_file}")
            self.state_machine.transition_to(DeploymentState.FAILED)
            return False
        
        self.audit_record.add_event("validate", "Parameters validated successfully")
        return True
    
    def _lint_template(self) -> bool:
        """Lint the Bicep template."""
        self.state_machine.transition_to(DeploymentState.LINTING)
        self.audit_record.add_event("lint", f"Linting template: {self.config.template_file}")
        
        result = self.linter.lint_file(self.config.template_file)
        
        # Log lint results
        self.audit_record.add_event("lint", "Lint complete", {
            "success": result.success,
            "errors": result.errors,
            "warnings": result.warnings
        })
        
        if result.has_errors():
            print("\n" + self.linter.format_results(result))
            self.state_machine.transition_to(DeploymentState.FAILED)
            
            # Classify failure
            error_msg = "\n".join([e.get("message", "") for e in result.errors])
            failure_type = self.failure_classifier.classify(error_msg)
            self.audit_record.add_event("failure_classification", f"Failure type: {failure_type.value}")
            
            return False
        
        if result.has_warnings():
            print("\n" + self.linter.format_results(result))
            if not self.config.allow_warnings:
                self.state_machine.transition_to(DeploymentState.FAILED)
                return False
        
        return True
    
    def _plan_deployment(self) -> bool:
        """Perform what-if planning."""
        self.state_machine.transition_to(DeploymentState.PLANNING)
        self.audit_record.add_event("plan", "Analyzing deployment changes")
        
        result = self.planner.analyze(
            resource_group=self.config.resource_group,
            template_file=self.config.template_file,
            parameters_file=self.config.parameters_file,
            location=self.config.location,
            parameter_overrides=self.config.parameter_overrides
        )
        
        # Log what-if results
        self.audit_record.add_event("plan", "What-if analysis complete", result.to_dict())
        
        print("\n" + self.planner.format_results(result))
        
        # Check for destructive changes
        if result.has_destructive_changes() and self.config.require_confirmation_for_deletes:
            self.state_machine.transition_to(DeploymentState.AWAITING_CONFIRMATION)
            self.audit_record.add_event("confirmation", "Awaiting user confirmation for destructive changes")
            
            print("\n⚠️  DESTRUCTIVE CHANGES DETECTED!")
            print("The following resources will be DELETED:")
            for change in result.get_destructive_changes():
                print(f"  - {change.resource_type}/{change.resource_name}")
            
            response = input("\nDo you want to proceed with these destructive changes? (yes/no): ")
            
            if response.lower() not in ["yes", "y"]:
                self.audit_record.add_event("confirmation", "User declined destructive changes")
                self.state_machine.transition_to(DeploymentState.FAILED)
                return False
            
            self.audit_record.add_event("confirmation", "User approved destructive changes")
        
        return True
    
    def _execute_deployment(self) -> bool:
        """Execute the deployment with retry logic."""
        self.state_machine.transition_to(DeploymentState.DEPLOYING)
        self.audit_record.add_event("deploy", f"Deploying to {self.config.resource_group}")
        
        max_attempts = 3
        for attempt in range(max_attempts):
            result = self._deploy_with_cli()
            
            if result[0]:
                self.audit_record.add_event("deploy", "Deployment succeeded", {"attempt": attempt + 1})
                return True
            
            # Capture the last error for propagation
            self.last_deploy_error = result[1] or ""
            
            # Classify failure
            failure_type = self.failure_classifier.classify(result[1])
            self.audit_record.add_event("deploy", f"Deployment failed (attempt {attempt + 1})", {
                "error": result[1],
                "failure_type": failure_type.value
            })
            
            # Determine if retry is appropriate
            if not self.failure_classifier.should_retry(failure_type):
                print(f"\n❌ Logic failure detected - no retry will be attempted")
                print(f"   Error: {result[1][:500] if result[1] else 'No error details'}")
                self.state_machine.transition_to(DeploymentState.FAILED)
                return False
            
            if attempt < max_attempts - 1:
                retry_strategy = self.failure_classifier.get_retry_strategy(failure_type, attempt)
                if retry_strategy["should_retry"]:
                    delay = retry_strategy["delay"]
                    print(f"\n🔄 Environmental failure - retrying in {delay} seconds...")
                    # Truncate to avoid overwhelming log output; full error is in audit record
                    max_error_len = 500
                    print(f"   Azure error: {result[1][:max_error_len] if result[1] else 'No error details'}")
                    import time
                    time.sleep(delay)
                else:
                    break
        
        self.state_machine.transition_to(DeploymentState.FAILED)
        return False
    
    def _deploy_with_cli(self) -> Tuple[bool, str]:
        """Execute deployment via Azure CLI."""
        deployment_name = f"aos-deploy-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"
        
        # Build command
        cmd = [
            "az", "deployment", "group", "create",
            "--name", deployment_name,
            "--resource-group", self.config.resource_group,
            "--template-file", str(self.config.template_file)
        ]
        
        # Add parameters
        if self.config.parameters_file:
            cmd.extend(["--parameters", str(self.config.parameters_file)])
        
        # Add parameter overrides
        for key, value in self.config.parameter_overrides.items():
            cmd.extend(["--parameters", f"{key}={value}"])
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=1800  # 30 minute timeout
            )
            
            if result.returncode == 0:
                # Parse output for resource IDs
                try:
                    output_data = json.loads(result.stdout)
                    outputs = output_data.get("properties", {}).get("outputs", {})
                    
                    # Extract resource IDs from outputs
                    for key, value in outputs.items():
                        if "Id" in key or "id" in key.lower():
                            resource_id = value.get("value", "")
                            if resource_id:
                                self.audit_record.add_resource(
                                    resource_id=resource_id,
                                    resource_type=key
                                )
                except json.JSONDecodeError:
                    pass
                
                return True, result.stdout
            else:
                return False, result.stderr or result.stdout
        
        except subprocess.TimeoutExpired:
            return False, "Deployment timed out after 30 minutes"
        except Exception as e:
            return False, f"Deployment error: {str(e)}"
    
    def _verify_health(self) -> bool:
        """Verify post-deployment health."""
        self.state_machine.transition_to(DeploymentState.VERIFYING_HEALTH)
        self.audit_record.add_event("health", "Verifying resource health")
        
        # Add health checks for deployed resources
        for resource in self.audit_record.resources:
            resource_id = resource["resource_id"]
            checker = AzureResourceHealthChecker(resource_id)
            self.health_verifier.add_checker(checker)
        
        # Run health checks
        all_healthy, results = self.health_verifier.verify_all()
        
        # Update audit record with health status
        for i, result in enumerate(results):
            if i < len(self.audit_record.resources):
                self.audit_record.resources[i]["health_status"] = result.status.value
        
        # Log health check results
        self.audit_record.add_event("health", "Health verification complete", {
            "all_healthy": all_healthy,
            "results": [r.to_dict() for r in results]
        })
        
        print("\n" + self.health_verifier.format_results(results))
        
        if not all_healthy:
            self.state_machine.transition_to(DeploymentState.FAILED)
            return False
        
        return True
