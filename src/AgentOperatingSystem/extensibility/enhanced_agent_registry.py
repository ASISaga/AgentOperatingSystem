"""
Enhanced Agent Registry Features for AgentOperatingSystem

Adds advanced capability discovery, dependency mapping, health status monitoring,
and upgrade orchestration to the existing AgentRegistry.
"""

from typing import Dict, Any, List, Optional, Set
from datetime import datetime, timedelta
from enum import Enum
import logging


class AgentHealth(str, Enum):
    """Agent health status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class AgentUpgradeStatus(str, Enum):
    """Agent upgrade status"""
    CURRENT = "current"
    UPDATE_AVAILABLE = "update_available"
    UPGRADING = "upgrading"
    UPGRADE_FAILED = "upgrade_failed"


class AgentDependency:
    """
    Represents a dependency between agents.
    """

    def __init__(
        self,
        dependent_agent_id: str,
        dependency_agent_id: str,
        dependency_type: str = "runtime",
        required: bool = True
    ):
        self.dependent_agent_id = dependent_agent_id
        self.dependency_agent_id = dependency_agent_id
        self.dependency_type = dependency_type  # runtime, build, optional
        self.required = required
        self.created_at = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "dependent_agent_id": self.dependent_agent_id,
            "dependency_agent_id": self.dependency_agent_id,
            "dependency_type": self.dependency_type,
            "required": self.required,
            "created_at": self.created_at.isoformat()
        }


class AgentCapability:
    """
    Represents a capability provided by an agent.
    """

    def __init__(
        self,
        capability_id: str,
        name: str,
        description: str,
        version: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.capability_id = capability_id
        self.name = name
        self.description = description
        self.version = version
        self.metadata = metadata or {}
        self.created_at = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "capability_id": self.capability_id,
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat()
        }


class AgentHealthCheck:
    """
    Represents a health check result for an agent.
    """

    def __init__(
        self,
        agent_id: str,
        status: AgentHealth,
        details: Optional[Dict[str, Any]] = None,
        checks_passed: int = 0,
        checks_failed: int = 0
    ):
        self.agent_id = agent_id
        self.status = status
        self.details = details or {}
        self.checks_passed = checks_passed
        self.checks_failed = checks_failed
        self.timestamp = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "agent_id": self.agent_id,
            "status": self.status.value,
            "details": self.details,
            "checks_passed": self.checks_passed,
            "checks_failed": self.checks_failed,
            "timestamp": self.timestamp.isoformat()
        }


class EnhancedAgentRegistry:
    """
    Enhanced agent registry with advanced capability discovery, dependency mapping,
    health monitoring, and upgrade orchestration.

    This extends the base AgentRegistry with P3 features from features.md.
    """

    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger("AOS.EnhancedAgentRegistry")

        # Capability discovery
        self.agent_capabilities: Dict[str, List[AgentCapability]] = {}  # agent_id -> capabilities
        self.capability_index: Dict[str, Set[str]] = {}  # capability_name -> agent_ids

        # Dependency mapping
        self.dependencies: Dict[str, List[AgentDependency]] = {}  # agent_id -> dependencies
        self.reverse_dependencies: Dict[str, Set[str]] = {}  # agent_id -> dependent_agent_ids

        # Health status
        self.health_checks: Dict[str, AgentHealthCheck] = {}  # agent_id -> latest health check
        self.health_history: Dict[str, List[AgentHealthCheck]] = {}  # agent_id -> health history

        # Upgrade orchestration
        self.upgrade_status: Dict[str, AgentUpgradeStatus] = {}  # agent_id -> upgrade status
        self.available_versions: Dict[str, List[str]] = {}  # agent_id -> available versions

    async def register_capability(
        self,
        agent_id: str,
        capability: AgentCapability
    ) -> bool:
        """
        Register a capability for an agent.

        Args:
            agent_id: Agent identifier
            capability: Capability to register

        Returns:
            True if successful
        """
        if agent_id not in self.agent_capabilities:
            self.agent_capabilities[agent_id] = []

        self.agent_capabilities[agent_id].append(capability)

        # Update capability index
        if capability.name not in self.capability_index:
            self.capability_index[capability.name] = set()
        self.capability_index[capability.name].add(agent_id)

        self.logger.info(
            f"Registered capability '{capability.name}' for agent {agent_id}"
        )

        return True

    async def discover_capabilities(self, capability_name: str) -> List[Dict[str, Any]]:
        """
        Discover all agents that provide a specific capability.

        Args:
            capability_name: Name of capability to search for

        Returns:
            List of agents with their capability details
        """
        if capability_name not in self.capability_index:
            return []

        agent_ids = self.capability_index[capability_name]
        results = []

        for agent_id in agent_ids:
            capabilities = self.agent_capabilities.get(agent_id, [])
            matching_caps = [
                c for c in capabilities
                if c.name == capability_name
            ]

            for cap in matching_caps:
                results.append({
                    "agent_id": agent_id,
                    "capability": cap.to_dict()
                })

        self.logger.debug(
            f"Discovered {len(results)} agents with capability '{capability_name}'"
        )

        return results

    async def get_agent_capabilities(self, agent_id: str) -> List[Dict[str, Any]]:
        """
        Get all capabilities for an agent.

        Args:
            agent_id: Agent identifier

        Returns:
            List of capability details
        """
        capabilities = self.agent_capabilities.get(agent_id, [])
        return [c.to_dict() for c in capabilities]

    async def add_dependency(
        self,
        dependent_agent_id: str,
        dependency_agent_id: str,
        dependency_type: str = "runtime",
        required: bool = True
    ) -> bool:
        """
        Add a dependency relationship between agents.

        Args:
            dependent_agent_id: Agent that has the dependency
            dependency_agent_id: Agent that is depended upon
            dependency_type: Type of dependency
            required: Whether this dependency is required

        Returns:
            True if successful
        """
        dependency = AgentDependency(
            dependent_agent_id=dependent_agent_id,
            dependency_agent_id=dependency_agent_id,
            dependency_type=dependency_type,
            required=required
        )

        if dependent_agent_id not in self.dependencies:
            self.dependencies[dependent_agent_id] = []

        self.dependencies[dependent_agent_id].append(dependency)

        # Update reverse dependencies
        if dependency_agent_id not in self.reverse_dependencies:
            self.reverse_dependencies[dependency_agent_id] = set()
        self.reverse_dependencies[dependency_agent_id].add(dependent_agent_id)

        self.logger.info(
            f"Added dependency: {dependent_agent_id} depends on {dependency_agent_id}"
        )

        return True

    async def get_dependencies(
        self,
        agent_id: str,
        include_optional: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Get all dependencies for an agent.

        Args:
            agent_id: Agent identifier
            include_optional: Whether to include optional dependencies

        Returns:
            List of dependency details
        """
        dependencies = self.dependencies.get(agent_id, [])

        if not include_optional:
            dependencies = [d for d in dependencies if d.required]

        return [d.to_dict() for d in dependencies]

    async def get_dependents(self, agent_id: str) -> List[str]:
        """
        Get all agents that depend on this agent.

        Args:
            agent_id: Agent identifier

        Returns:
            List of dependent agent IDs
        """
        return list(self.reverse_dependencies.get(agent_id, set()))

    async def get_dependency_tree(
        self,
        agent_id: str,
        max_depth: int = 5
    ) -> Dict[str, Any]:
        """
        Get the full dependency tree for an agent.

        Args:
            agent_id: Agent identifier
            max_depth: Maximum depth to traverse

        Returns:
            Dependency tree structure
        """
        def build_tree(current_id: str, depth: int, visited: Set[str]) -> Dict[str, Any]:
            if depth >= max_depth or current_id in visited:
                return {"agent_id": current_id, "dependencies": []}

            visited.add(current_id)
            dependencies = self.dependencies.get(current_id, [])

            tree = {
                "agent_id": current_id,
                "dependencies": []
            }

            for dep in dependencies:
                subtree = build_tree(dep.dependency_agent_id, depth + 1, visited)
                tree["dependencies"].append({
                    "dependency": dep.to_dict(),
                    "tree": subtree
                })

            return tree

        return build_tree(agent_id, 0, set())

    async def record_health_check(
        self,
        agent_id: str,
        status: AgentHealth,
        details: Optional[Dict[str, Any]] = None,
        checks_passed: int = 0,
        checks_failed: int = 0
    ) -> bool:
        """
        Record a health check result for an agent.

        Args:
            agent_id: Agent identifier
            status: Health status
            details: Optional details about the health check
            checks_passed: Number of checks that passed
            checks_failed: Number of checks that failed

        Returns:
            True if successful
        """
        health_check = AgentHealthCheck(
            agent_id=agent_id,
            status=status,
            details=details,
            checks_passed=checks_passed,
            checks_failed=checks_failed
        )

        # Store latest health check
        self.health_checks[agent_id] = health_check

        # Add to history
        if agent_id not in self.health_history:
            self.health_history[agent_id] = []
        self.health_history[agent_id].append(health_check)

        # Keep only last 100 health checks per agent
        if len(self.health_history[agent_id]) > 100:
            self.health_history[agent_id] = self.health_history[agent_id][-100:]

        self.logger.info(f"Recorded health check for {agent_id}: {status.value}")

        return True

    async def get_health_status(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the latest health status for an agent.

        Args:
            agent_id: Agent identifier

        Returns:
            Health check details or None
        """
        health_check = self.health_checks.get(agent_id)
        return health_check.to_dict() if health_check else None

    async def get_unhealthy_agents(self) -> List[Dict[str, Any]]:
        """
        Get all agents with unhealthy or degraded status.

        Returns:
            List of unhealthy agents with details
        """
        unhealthy = []

        for agent_id, health_check in self.health_checks.items():
            if health_check.status in [AgentHealth.UNHEALTHY, AgentHealth.DEGRADED]:
                unhealthy.append({
                    "agent_id": agent_id,
                    "health_check": health_check.to_dict()
                })

        return unhealthy

    async def set_upgrade_status(
        self,
        agent_id: str,
        status: AgentUpgradeStatus,
        available_versions: Optional[List[str]] = None
    ) -> bool:
        """
        Set upgrade status for an agent.

        Args:
            agent_id: Agent identifier
            status: Upgrade status
            available_versions: Optional list of available versions

        Returns:
            True if successful
        """
        self.upgrade_status[agent_id] = status

        if available_versions:
            self.available_versions[agent_id] = available_versions

        self.logger.info(f"Set upgrade status for {agent_id}: {status.value}")

        return True

    async def get_upgrade_status(self, agent_id: str) -> Optional[str]:
        """
        Get upgrade status for an agent.

        Args:
            agent_id: Agent identifier

        Returns:
            Upgrade status or None
        """
        status = self.upgrade_status.get(agent_id)
        return status.value if status else None

    async def get_agents_needing_upgrade(self) -> List[Dict[str, Any]]:
        """
        Get all agents that have updates available.

        Returns:
            List of agents with available upgrades
        """
        agents_to_upgrade = []

        for agent_id, status in self.upgrade_status.items():
            if status == AgentUpgradeStatus.UPDATE_AVAILABLE:
                agents_to_upgrade.append({
                    "agent_id": agent_id,
                    "status": status.value,
                    "available_versions": self.available_versions.get(agent_id, [])
                })

        return agents_to_upgrade

    async def orchestrate_upgrade(
        self,
        agent_id: str,
        target_version: str
    ) -> Dict[str, Any]:
        """
        Orchestrate an upgrade for an agent.

        This is a placeholder that would coordinate the actual upgrade process.

        Args:
            agent_id: Agent to upgrade
            target_version: Version to upgrade to

        Returns:
            Upgrade result
        """
        result = {
            "agent_id": agent_id,
            "target_version": target_version,
            "status": "pending",
            "started_at": datetime.utcnow().isoformat()
        }

        try:
            # Set upgrading status
            await self.set_upgrade_status(agent_id, AgentUpgradeStatus.UPGRADING)

            # Check dependencies
            dependencies = await self.get_dependencies(agent_id)
            result["dependencies_checked"] = len(dependencies)

            # Check dependents
            dependents = await self.get_dependents(agent_id)
            result["dependents_notified"] = len(dependents)

            # In a real implementation, this would:
            # 1. Validate target version compatibility
            # 2. Check if dependents support the new version
            # 3. Coordinate the upgrade process
            # 4. Verify post-upgrade health
            # 5. Rollback if necessary

            # Simulate successful upgrade
            await self.set_upgrade_status(agent_id, AgentUpgradeStatus.CURRENT)

            result["status"] = "completed"
            result["completed_at"] = datetime.utcnow().isoformat()

            self.logger.info(
                f"Orchestrated upgrade for {agent_id} to version {target_version}"
            )

        except Exception as e:
            await self.set_upgrade_status(agent_id, AgentUpgradeStatus.UPGRADE_FAILED)
            result["status"] = "failed"
            result["error"] = str(e)
            self.logger.error(f"Upgrade failed for {agent_id}: {e}")

        return result

    def get_registry_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive summary of the registry.

        Returns:
            Summary report
        """
        total_agents = len(set(
            list(self.agent_capabilities.keys()) +
            list(self.dependencies.keys()) +
            list(self.health_checks.keys())
        ))

        health_summary = {
            status.value: 0 for status in AgentHealth
        }
        for health_check in self.health_checks.values():
            health_summary[health_check.status.value] += 1

        upgrade_summary = {
            status.value: 0 for status in AgentUpgradeStatus
        }
        for status in self.upgrade_status.values():
            upgrade_summary[status.value] += 1

        return {
            "total_agents": total_agents,
            "total_capabilities": sum(len(caps) for caps in self.agent_capabilities.values()),
            "total_dependencies": sum(len(deps) for deps in self.dependencies.values()),
            "health_summary": health_summary,
            "upgrade_summary": upgrade_summary,
            "generated_at": datetime.utcnow().isoformat()
        }
