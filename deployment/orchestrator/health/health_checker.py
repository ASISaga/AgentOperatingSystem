"""
Health Checkers

Post-deployment health verification for Azure resources.
"""

import subprocess
import socket
import time
import json
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from enum import Enum
import urllib.request
import urllib.error


class HealthStatus(Enum):
    """Health check status."""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"
    UNKNOWN = "unknown"


class HealthCheckResult:
    """Result of a health check."""
    
    def __init__(self, check_name: str, status: HealthStatus, 
                 message: str, details: Optional[Dict[str, Any]] = None):
        """
        Initialize health check result.
        
        Args:
            check_name: Name of the health check
            status: Health status
            message: Status message
            details: Additional details
        """
        self.check_name = check_name
        self.status = status
        self.message = message
        self.details = details or {}
    
    def is_healthy(self) -> bool:
        """Check if result is healthy."""
        return self.status == HealthStatus.HEALTHY
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "check_name": self.check_name,
            "status": self.status.value,
            "message": self.message,
            "is_healthy": self.is_healthy(),
            "details": self.details
        }


class HealthChecker:
    """
    Base class for health checkers.
    """
    
    def check(self) -> HealthCheckResult:
        """Perform health check."""
        raise NotImplementedError


class TCPHealthChecker(HealthChecker):
    """TCP port connectivity health check."""
    
    def __init__(self, host: str, port: int, timeout: int = 5):
        """
        Initialize TCP health checker.
        
        Args:
            host: Hostname or IP address
            port: Port number
            timeout: Connection timeout in seconds
        """
        self.host = host
        self.port = port
        self.timeout = timeout
    
    def check(self) -> HealthCheckResult:
        """Check TCP connectivity."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            result = sock.connect_ex((self.host, self.port))
            sock.close()
            
            if result == 0:
                return HealthCheckResult(
                    check_name=f"TCP:{self.host}:{self.port}",
                    status=HealthStatus.HEALTHY,
                    message=f"Port {self.port} is reachable",
                    details={"host": self.host, "port": self.port}
                )
            else:
                return HealthCheckResult(
                    check_name=f"TCP:{self.host}:{self.port}",
                    status=HealthStatus.UNHEALTHY,
                    message=f"Port {self.port} is not reachable",
                    details={"host": self.host, "port": self.port, "error_code": result}
                )
        except Exception as e:
            return HealthCheckResult(
                check_name=f"TCP:{self.host}:{self.port}",
                status=HealthStatus.UNHEALTHY,
                message=f"Error checking TCP connectivity: {str(e)}",
                details={"host": self.host, "port": self.port, "error": str(e)}
            )


class HTTPHealthChecker(HealthChecker):
    """HTTP endpoint health check."""
    
    def __init__(self, url: str, expected_status: int = 200, timeout: int = 10):
        """
        Initialize HTTP health checker.
        
        Args:
            url: HTTP/HTTPS URL to check
            expected_status: Expected HTTP status code
            timeout: Request timeout in seconds
        """
        self.url = url
        self.expected_status = expected_status
        self.timeout = timeout
    
    def check(self) -> HealthCheckResult:
        """Check HTTP endpoint."""
        try:
            req = urllib.request.Request(self.url, method='GET')
            response = urllib.request.urlopen(req, timeout=self.timeout)
            status_code = response.getcode()
            
            if status_code == self.expected_status:
                return HealthCheckResult(
                    check_name=f"HTTP:{self.url}",
                    status=HealthStatus.HEALTHY,
                    message=f"HTTP {status_code} received (expected {self.expected_status})",
                    details={"url": self.url, "status_code": status_code}
                )
            else:
                return HealthCheckResult(
                    check_name=f"HTTP:{self.url}",
                    status=HealthStatus.DEGRADED,
                    message=f"HTTP {status_code} received (expected {self.expected_status})",
                    details={"url": self.url, "status_code": status_code}
                )
        except urllib.error.HTTPError as e:
            return HealthCheckResult(
                check_name=f"HTTP:{self.url}",
                status=HealthStatus.UNHEALTHY,
                message=f"HTTP error: {e.code} {e.reason}",
                details={"url": self.url, "status_code": e.code, "error": str(e)}
            )
        except Exception as e:
            return HealthCheckResult(
                check_name=f"HTTP:{self.url}",
                status=HealthStatus.UNHEALTHY,
                message=f"Error checking HTTP endpoint: {str(e)}",
                details={"url": self.url, "error": str(e)}
            )


class AzureResourceHealthChecker(HealthChecker):
    """Azure Resource Health API check."""
    
    def __init__(self, resource_id: str):
        """
        Initialize Azure resource health checker.
        
        Args:
            resource_id: Full Azure resource ID
        """
        self.resource_id = resource_id
    
    def check(self) -> HealthCheckResult:
        """Check Azure resource health via CLI."""
        try:
            # Use Azure CLI to get resource health
            result = subprocess.run(
                ["az", "resource", "show", "--ids", self.resource_id],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                try:
                    resource_data = json.loads(result.stdout)
                    provisioning_state = resource_data.get("properties", {}).get("provisioningState", "Unknown")
                    
                    if provisioning_state == "Succeeded":
                        return HealthCheckResult(
                            check_name=f"AzureResource:{self.resource_id}",
                            status=HealthStatus.HEALTHY,
                            message=f"Resource provisioned successfully",
                            details={"resource_id": self.resource_id, "provisioning_state": provisioning_state}
                        )
                    elif provisioning_state in ["Creating", "Updating"]:
                        return HealthCheckResult(
                            check_name=f"AzureResource:{self.resource_id}",
                            status=HealthStatus.DEGRADED,
                            message=f"Resource is being provisioned: {provisioning_state}",
                            details={"resource_id": self.resource_id, "provisioning_state": provisioning_state}
                        )
                    else:
                        return HealthCheckResult(
                            check_name=f"AzureResource:{self.resource_id}",
                            status=HealthStatus.UNHEALTHY,
                            message=f"Resource provisioning state: {provisioning_state}",
                            details={"resource_id": self.resource_id, "provisioning_state": provisioning_state}
                        )
                except json.JSONDecodeError:
                    return HealthCheckResult(
                        check_name=f"AzureResource:{self.resource_id}",
                        status=HealthStatus.UNKNOWN,
                        message="Failed to parse resource data",
                        details={"resource_id": self.resource_id}
                    )
            else:
                return HealthCheckResult(
                    check_name=f"AzureResource:{self.resource_id}",
                    status=HealthStatus.UNHEALTHY,
                    message=f"Failed to get resource: {result.stderr}",
                    details={"resource_id": self.resource_id, "error": result.stderr}
                )
        except subprocess.TimeoutExpired:
            return HealthCheckResult(
                check_name=f"AzureResource:{self.resource_id}",
                status=HealthStatus.UNKNOWN,
                message="Health check timed out",
                details={"resource_id": self.resource_id}
            )
        except Exception as e:
            return HealthCheckResult(
                check_name=f"AzureResource:{self.resource_id}",
                status=HealthStatus.UNKNOWN,
                message=f"Error checking resource health: {str(e)}",
                details={"resource_id": self.resource_id, "error": str(e)}
            )


class HealthVerifier:
    """
    Orchestrates multiple health checks.
    """
    
    def __init__(self, max_retries: int = 3, retry_delay: int = 10):
        """
        Initialize health verifier.
        
        Args:
            max_retries: Maximum number of retries for failed checks
            retry_delay: Delay between retries in seconds
        """
        self.checkers: List[HealthChecker] = []
        self.max_retries = max_retries
        self.retry_delay = retry_delay
    
    def add_checker(self, checker: HealthChecker):
        """Add a health checker."""
        self.checkers.append(checker)
    
    def verify_all(self) -> Tuple[bool, List[HealthCheckResult]]:
        """
        Run all health checks with retries.
        
        Returns:
            Tuple of (all_healthy, results)
        """
        results = []
        
        for checker in self.checkers:
            result = self._check_with_retry(checker)
            results.append(result)
        
        all_healthy = all(r.is_healthy() for r in results)
        return all_healthy, results
    
    def _check_with_retry(self, checker: HealthChecker) -> HealthCheckResult:
        """
        Execute a health check with retries.
        
        Args:
            checker: Health checker to run
            
        Returns:
            HealthCheckResult
        """
        for attempt in range(self.max_retries):
            result = checker.check()
            
            if result.is_healthy():
                return result
            
            # Retry on unhealthy or degraded
            if attempt < self.max_retries - 1:
                time.sleep(self.retry_delay)
        
        return result
    
    def format_results(self, results: List[HealthCheckResult]) -> str:
        """
        Format health check results.
        
        Args:
            results: List of health check results
            
        Returns:
            Formatted string
        """
        lines = []
        lines.append("=" * 60)
        lines.append("HEALTH CHECK RESULTS")
        lines.append("=" * 60)
        
        healthy_count = sum(1 for r in results if r.is_healthy())
        total_count = len(results)
        
        lines.append(f"\nOverall: {healthy_count}/{total_count} checks passed")
        
        for result in results:
            status_icon = "✅" if result.is_healthy() else "❌"
            lines.append(f"\n{status_icon} {result.check_name}")
            lines.append(f"   Status: {result.status.value}")
            lines.append(f"   Message: {result.message}")
        
        lines.append("\n" + "=" * 60)
        
        return "\n".join(lines)
