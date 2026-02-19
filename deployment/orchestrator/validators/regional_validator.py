"""
Regional Capability Validator

Validates Azure region capabilities and recommends optimal regions for AOS deployment.
Ensures service availability and provides intelligent fallback mechanisms.
"""

from typing import Dict, List, Set, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum


class ServiceType(Enum):
    """Azure service types used by AOS."""
    STORAGE = "storage"
    KEY_VAULT = "keyvault"
    FUNCTIONS_CONSUMPTION = "functions_consumption"
    FUNCTIONS_PREMIUM = "functions_premium"
    SERVICE_BUS_BASIC = "servicebus_basic"
    SERVICE_BUS_STANDARD = "servicebus_standard"
    SERVICE_BUS_PREMIUM = "servicebus_premium"
    APP_INSIGHTS = "appinsights"
    LOG_ANALYTICS = "loganalytics"
    AZURE_ML = "azureml"
    CONTAINER_REGISTRY = "acr"
    MANAGED_IDENTITY = "managedidentity"


class RegionTier(Enum):
    """Region capability tiers."""
    TIER_1 = "tier1"  # Full capability - all services
    TIER_2 = "tier2"  # Good coverage - most services
    TIER_3 = "tier3"  # Basic coverage - core services only
    UNKNOWN = "unknown"


@dataclass
class RegionalCapability:
    """Represents service availability in a region."""
    region: str
    tier: RegionTier
    available_services: Set[ServiceType]
    unavailable_services: Set[ServiceType]
    
    def supports_service(self, service: ServiceType) -> bool:
        """Check if region supports a service."""
        return service in self.available_services
    
    def compatibility_score(self, required_services: Set[ServiceType]) -> float:
        """
        Calculate compatibility score (0.0 to 1.0).
        
        Args:
            required_services: Set of required services
            
        Returns:
            Score from 0.0 (no services) to 1.0 (all services)
        """
        if not required_services:
            return 1.0
        
        supported = len(required_services & self.available_services)
        return supported / len(required_services)


class RegionalValidator:
    """
    Validates Azure region capabilities for AOS deployment.
    
    Provides:
    - Service availability checks
    - Region recommendations
    - Compatibility scoring
    - Automatic fallback suggestions
    """
    
    # Regions with full Azure ML and AI Services support (as of Feb 2026)
    AZURE_ML_REGIONS = {
        'eastus', 'eastus2', 'westus2', 'westus3',
        'northcentralus', 'southcentralus',
        'westeurope', 'northeurope', 'uksouth', 'francecentral',
        'germanywestcentral', 'switzerlandnorth', 'swedencentral',
        'southeastasia', 'japaneast', 'australiaeast',
        'canadacentral', 'koreacentral', 'centralindia'
    }
    
    # Regions with Azure Functions Premium (EP) support
    FUNCTIONS_PREMIUM_REGIONS = {
        'eastus', 'eastus2', 'westus', 'westus2', 'westus3',
        'centralus', 'northcentralus', 'southcentralus', 'westcentralus',
        'canadacentral', 'canadaeast', 'brazilsouth',
        'northeurope', 'westeurope', 'uksouth', 'ukwest',
        'francecentral', 'germanywestcentral', 'switzerlandnorth',
        'norwayeast', 'swedencentral',
        'southeastasia', 'eastasia', 'australiaeast', 'australiasoutheast',
        'japaneast', 'japanwest', 'koreacentral',
        'centralindia', 'southindia', 'southafricanorth', 'uaenorth'
    }
    
    # Regions with Service Bus Premium support
    SERVICE_BUS_PREMIUM_REGIONS = {
        'eastus', 'eastus2', 'westus', 'westus2', 'westus3',
        'centralus', 'northcentralus', 'southcentralus', 'westcentralus',
        'canadacentral', 'canadaeast', 'brazilsouth',
        'northeurope', 'westeurope', 'uksouth', 'ukwest',
        'francecentral', 'germanywestcentral', 'switzerlandnorth',
        'norwayeast', 'swedencentral',
        'southeastasia', 'eastasia', 'australiaeast', 'australiasoutheast',
        'japaneast', 'japanwest', 'koreacentral',
        'centralindia', 'southindia', 'southafricanorth', 'uaenorth'
    }
    
    # Tier 1 regions - full capability (all services including Azure ML)
    TIER_1_REGIONS = {
        'eastus', 'eastus2', 'westus2',  # Americas
        'westeurope', 'northeurope',  # Europe
        'southeastasia', 'australiaeast', 'japaneast'  # Asia Pacific
    }
    
    # Tier 2 regions - good coverage (most services, may lack some premium features)
    TIER_2_REGIONS = {
        'westus3', 'canadacentral',  # Americas
        'uksouth', 'francecentral', 'swedencentral',  # Europe
        'koreacentral', 'centralindia'  # Asia Pacific
    }
    
    # All allowed regions (from Bicep template)
    ALL_REGIONS = {
        'eastus', 'eastus2', 'westus', 'westus2', 'westus3',
        'centralus', 'northcentralus', 'southcentralus', 'westcentralus',
        'northeurope', 'westeurope', 'uksouth', 'ukwest',
        'francecentral', 'germanywestcentral', 'switzerlandnorth',
        'norwayeast', 'swedencentral',
        'southeastasia', 'eastasia', 'japaneast', 'japanwest',
        'koreacentral', 'australiaeast', 'australiasoutheast',
        'canadacentral', 'canadaeast', 'brazilsouth',
        'southafricanorth', 'uaenorth', 'centralindia', 'southindia'
    }
    
    def __init__(self):
        """Initialize the regional validator."""
        self._capability_cache: Dict[str, RegionalCapability] = {}
    
    def get_region_capability(self, region: str) -> RegionalCapability:
        """
        Get capability information for a region.
        
        Args:
            region: Azure region name (e.g., 'eastus')
            
        Returns:
            RegionalCapability object
        """
        # Check cache
        if region in self._capability_cache:
            return self._capability_cache[region]
        
        # Determine tier
        if region in self.TIER_1_REGIONS:
            tier = RegionTier.TIER_1
        elif region in self.TIER_2_REGIONS:
            tier = RegionTier.TIER_2
        elif region in self.ALL_REGIONS:
            tier = RegionTier.TIER_3
        else:
            tier = RegionTier.UNKNOWN
        
        # Determine available services
        available = set()
        unavailable = set()
        
        # Core services - available in all regions
        core_services = {
            ServiceType.STORAGE,
            ServiceType.KEY_VAULT,
            ServiceType.FUNCTIONS_CONSUMPTION,
            ServiceType.SERVICE_BUS_BASIC,
            ServiceType.SERVICE_BUS_STANDARD,
            ServiceType.MANAGED_IDENTITY
        }
        available.update(core_services)
        
        # App Insights and Log Analytics - most regions
        if tier != RegionTier.UNKNOWN:
            available.add(ServiceType.APP_INSIGHTS)
            available.add(ServiceType.LOG_ANALYTICS)
        
        # Functions Premium
        if region in self.FUNCTIONS_PREMIUM_REGIONS:
            available.add(ServiceType.FUNCTIONS_PREMIUM)
        else:
            unavailable.add(ServiceType.FUNCTIONS_PREMIUM)
        
        # Service Bus Premium
        if region in self.SERVICE_BUS_PREMIUM_REGIONS:
            available.add(ServiceType.SERVICE_BUS_PREMIUM)
        else:
            unavailable.add(ServiceType.SERVICE_BUS_PREMIUM)
        
        # Azure ML and Container Registry
        if region in self.AZURE_ML_REGIONS:
            available.add(ServiceType.AZURE_ML)
            available.add(ServiceType.CONTAINER_REGISTRY)
        else:
            unavailable.add(ServiceType.AZURE_ML)
            unavailable.add(ServiceType.CONTAINER_REGISTRY)
        
        capability = RegionalCapability(
            region=region,
            tier=tier,
            available_services=available,
            unavailable_services=unavailable
        )
        
        # Cache result
        self._capability_cache[region] = capability
        return capability
    
    def validate_region(self, region: str, required_services: Set[ServiceType]) -> Tuple[bool, List[str]]:
        """
        Validate if a region can support required services.
        
        Args:
            region: Azure region to validate
            required_services: Set of required services
            
        Returns:
            Tuple of (is_valid, list_of_warnings)
        """
        capability = self.get_region_capability(region)
        warnings = []
        
        # Check if region is known
        if capability.tier == RegionTier.UNKNOWN:
            warnings.append(f"Region '{region}' is not in the list of supported regions")
            return False, warnings
        
        # Check each required service
        missing_services = []
        for service in required_services:
            if not capability.supports_service(service):
                missing_services.append(service.value)
        
        if missing_services:
            warnings.append(
                f"Region '{region}' does not support: {', '.join(missing_services)}"
            )
            
            # Suggest what will happen
            if ServiceType.AZURE_ML in required_services and not capability.supports_service(ServiceType.AZURE_ML):
                warnings.append("→ Azure ML deployment will be automatically disabled")
            
            if ServiceType.FUNCTIONS_PREMIUM in required_services and not capability.supports_service(ServiceType.FUNCTIONS_PREMIUM):
                warnings.append("→ Functions will automatically downgrade to Consumption (Y1)")
            
            if ServiceType.SERVICE_BUS_PREMIUM in required_services and not capability.supports_service(ServiceType.SERVICE_BUS_PREMIUM):
                warnings.append("→ Service Bus will automatically downgrade to Standard")
        
        # Warn about tier
        if capability.tier == RegionTier.TIER_3:
            warnings.append(f"Region '{region}' is Tier 3 (basic coverage) - consider Tier 1 region for production")
        
        return len(missing_services) == 0, warnings
    
    def recommend_regions(self, required_services: Set[ServiceType], 
                         preferred_geography: Optional[str] = None,
                         limit: int = 5) -> List[Tuple[str, float, RegionTier]]:
        """
        Recommend regions based on required services.
        
        Args:
            required_services: Set of required services
            preferred_geography: Optional geographic preference ('americas', 'europe', 'asia')
            limit: Maximum number of recommendations
            
        Returns:
            List of tuples (region, compatibility_score, tier) sorted by score descending
        """
        recommendations = []
        
        for region in self.ALL_REGIONS:
            capability = self.get_region_capability(region)
            score = capability.compatibility_score(required_services)
            
            # Boost score for tier 1 regions
            if capability.tier == RegionTier.TIER_1:
                score += 0.1
            elif capability.tier == RegionTier.TIER_2:
                score += 0.05
            
            # Boost score for preferred geography
            if preferred_geography:
                if self._matches_geography(region, preferred_geography):
                    score += 0.05
            
            recommendations.append((region, min(score, 1.0), capability.tier))
        
        # Sort by score descending, then by tier
        tier_order = {RegionTier.TIER_1: 0, RegionTier.TIER_2: 1, RegionTier.TIER_3: 2, RegionTier.UNKNOWN: 3}
        recommendations.sort(key=lambda x: (-x[1], tier_order[x[2]]))
        
        return recommendations[:limit]
    
    def _matches_geography(self, region: str, geography: str) -> bool:
        """Check if region matches geographic preference."""
        geography = geography.lower()
        
        americas = {'eastus', 'eastus2', 'westus', 'westus2', 'westus3',
                   'centralus', 'northcentralus', 'southcentralus', 'westcentralus',
                   'canadacentral', 'canadaeast', 'brazilsouth'}
        
        europe = {'northeurope', 'westeurope', 'uksouth', 'ukwest',
                 'francecentral', 'germanywestcentral', 'switzerlandnorth',
                 'norwayeast', 'swedencentral'}
        
        asia = {'southeastasia', 'eastasia', 'japaneast', 'japanwest',
               'koreacentral', 'australiaeast', 'australiasoutheast',
               'centralindia', 'southindia', 'southafricanorth', 'uaenorth'}
        
        if geography in ('americas', 'america', 'us', 'na'):
            return region in americas
        elif geography in ('europe', 'eu', 'emea'):
            return region in europe
        elif geography in ('asia', 'apac', 'asiapacific'):
            return region in asia
        
        return False
    
    def get_best_alternative(self, current_region: str, 
                            required_services: Set[ServiceType]) -> Optional[str]:
        """
        Find the best alternative region if current region is incompatible.
        
        Args:
            current_region: Current region that may be incompatible
            required_services: Required services
            
        Returns:
            Best alternative region name, or None if current is good
        """
        # Check if current region is compatible
        is_valid, _ = self.validate_region(current_region, required_services)
        
        if is_valid:
            return None  # Current region is fine
        
        # Try to preserve geography
        geography = None
        if current_region in self._get_geography_regions('americas'):
            geography = 'americas'
        elif current_region in self._get_geography_regions('europe'):
            geography = 'europe'
        elif current_region in self._get_geography_regions('asia'):
            geography = 'asia'
        
        # Get recommendations
        recommendations = self.recommend_regions(required_services, geography, limit=3)
        
        if recommendations:
            return recommendations[0][0]  # Return best match
        
        return None
    
    def _get_geography_regions(self, geography: str) -> Set[str]:
        """Get all regions for a geography."""
        if geography == 'americas':
            return {'eastus', 'eastus2', 'westus', 'westus2', 'westus3',
                   'centralus', 'northcentralus', 'southcentralus', 'westcentralus',
                   'canadacentral', 'canadaeast', 'brazilsouth'}
        elif geography == 'europe':
            return {'northeurope', 'westeurope', 'uksouth', 'ukwest',
                   'francecentral', 'germanywestcentral', 'switzerlandnorth',
                   'norwayeast', 'swedencentral'}
        elif geography == 'asia':
            return {'southeastasia', 'eastasia', 'japaneast', 'japanwest',
                   'koreacentral', 'australiaeast', 'australiasoutheast',
                   'centralindia', 'southindia', 'southafricanorth', 'uaenorth'}
        return set()
    
    def generate_deployment_summary(self, region: str, 
                                   required_services: Set[ServiceType]) -> Dict[str, Any]:
        """
        Generate a deployment summary for reporting.
        
        Args:
            region: Target region
            required_services: Required services
            
        Returns:
            Dictionary with deployment summary
        """
        capability = self.get_region_capability(region)
        is_valid, warnings = self.validate_region(region, required_services)
        
        supported = []
        unsupported = []
        
        for service in required_services:
            if capability.supports_service(service):
                supported.append(service.value)
            else:
                unsupported.append(service.value)
        
        return {
            'region': region,
            'tier': capability.tier.value,
            'is_valid': is_valid,
            'compatibility_score': capability.compatibility_score(required_services),
            'supported_services': supported,
            'unsupported_services': unsupported,
            'warnings': warnings,
            'recommended_alternatives': [
                {'region': r, 'score': s, 'tier': t.value}
                for r, s, t in self.recommend_regions(required_services, limit=3)
            ] if unsupported else []
        }
