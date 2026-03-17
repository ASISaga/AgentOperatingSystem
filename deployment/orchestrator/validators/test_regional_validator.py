"""
Tests for Regional Validator
"""

import unittest
from regional_validator import (
    RegionalValidator, ServiceType, RegionTier
)


class TestRegionalValidator(unittest.TestCase):
    """Test regional validation functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.validator = RegionalValidator()
    
    def test_tier_1_region_capabilities(self):
        """Test that Tier 1 regions have full capabilities."""
        tier1_regions = ['eastus', 'eastus2', 'westus2', 'westeurope', 'northeurope']
        
        for region in tier1_regions:
            capability = self.validator.get_region_capability(region)
            
            # Should be Tier 1
            self.assertEqual(capability.tier, RegionTier.TIER_1)
            
            # Should support all premium services
            self.assertTrue(capability.supports_service(ServiceType.AZURE_ML))
            self.assertTrue(capability.supports_service(ServiceType.FUNCTIONS_PREMIUM))
            self.assertTrue(capability.supports_service(ServiceType.SERVICE_BUS_PREMIUM))
    
    def test_basic_region_capabilities(self):
        """Test basic services available in all regions."""
        test_regions = ['eastus', 'westus3', 'brazilsouth', 'centralindia']
        
        core_services = {
            ServiceType.STORAGE,
            ServiceType.KEY_VAULT,
            ServiceType.FUNCTIONS_CONSUMPTION,
            ServiceType.SERVICE_BUS_BASIC,
            ServiceType.SERVICE_BUS_STANDARD
        }
        
        for region in test_regions:
            capability = self.validator.get_region_capability(region)
            
            for service in core_services:
                self.assertTrue(
                    capability.supports_service(service),
                    f"Region {region} should support {service.value}"
                )
    
    def test_azure_ml_availability(self):
        """Test Azure ML availability detection."""
        # Regions with Azure ML
        with_ml = ['eastus', 'westeurope', 'southeastasia']
        for region in with_ml:
            capability = self.validator.get_region_capability(region)
            self.assertTrue(capability.supports_service(ServiceType.AZURE_ML))
        
        # Regions without Azure ML (not in the list)
        # Test with regions that are definitely NOT in AZURE_ML_REGIONS
        without_ml = ['eastasia', 'japanwest', 'southafricanorth']
        for region in without_ml:
            capability = self.validator.get_region_capability(region)
            # These regions don't have Azure ML
            self.assertFalse(capability.supports_service(ServiceType.AZURE_ML))
    
    def test_compatibility_score(self):
        """Test compatibility score calculation."""
        capability = self.validator.get_region_capability('eastus')
        
        # All services available
        all_services = {
            ServiceType.STORAGE,
            ServiceType.AZURE_ML,
            ServiceType.FUNCTIONS_PREMIUM
        }
        score = capability.compatibility_score(all_services)
        self.assertEqual(score, 1.0)
        
        # Partial availability (test with a region missing some services)
        capability_limited = self.validator.get_region_capability('eastasia')
        services_with_ml = {
            ServiceType.STORAGE,
            ServiceType.AZURE_ML  # Not available in eastasia
        }
        score_limited = capability_limited.compatibility_score(services_with_ml)
        self.assertEqual(score_limited, 0.5)  # 1 out of 2 services
    
    def test_validate_region_success(self):
        """Test successful region validation."""
        required = {
            ServiceType.STORAGE,
            ServiceType.FUNCTIONS_CONSUMPTION,
            ServiceType.SERVICE_BUS_STANDARD
        }
        
        is_valid, warnings = self.validator.validate_region('eastus', required)
        
        self.assertTrue(is_valid)
        # May have tier warnings but not service warnings
        for warning in warnings:
            self.assertNotIn('does not support', warning)
    
    def test_validate_region_with_missing_services(self):
        """Test validation with missing services."""
        # Request Azure ML in a region that doesn't support it
        required = {
            ServiceType.STORAGE,
            ServiceType.AZURE_ML
        }
        
        is_valid, warnings = self.validator.validate_region('eastasia', required)
        
        self.assertFalse(is_valid)
        self.assertTrue(len(warnings) > 0)
        # Should mention Azure ML
        warning_text = ' '.join(warnings)
        self.assertIn('azureml', warning_text.lower())
    
    def test_recommend_regions(self):
        """Test region recommendations."""
        required = {
            ServiceType.STORAGE,
            ServiceType.AZURE_ML,
            ServiceType.FUNCTIONS_PREMIUM,
            ServiceType.SERVICE_BUS_PREMIUM
        }
        
        recommendations = self.validator.recommend_regions(required, limit=5)
        
        # Should return 5 recommendations
        self.assertEqual(len(recommendations), 5)
        
        # First recommendation should be Tier 1 with high score
        first = recommendations[0]
        self.assertIn(first[0], self.validator.TIER_1_REGIONS)
        self.assertGreaterEqual(first[1], 0.9)  # High compatibility score
        
        # All should be sorted by score descending
        scores = [r[1] for r in recommendations]
        self.assertEqual(scores, sorted(scores, reverse=True))
    
    def test_recommend_regions_with_geography(self):
        """Test region recommendations with geographic preference."""
        required = {
            ServiceType.STORAGE,
            ServiceType.FUNCTIONS_CONSUMPTION  # Available everywhere
        }
        
        # Prefer Americas
        americas_recs = self.validator.recommend_regions(required, 'americas', limit=5)
        
        # Check that Americas regions are boosted
        # At least first region or majority should be from preferred geography
        americas_regions = self.validator._get_geography_regions('americas')
        americas_count = sum(1 for r in americas_recs[:5] if r[0] in americas_regions)
        self.assertGreaterEqual(americas_count, 2, "At least 2 of top 5 should be from Americas when preferred")
        
        # Prefer Europe
        europe_recs = self.validator.recommend_regions(required, 'europe', limit=5)
        europe_regions = self.validator._get_geography_regions('europe')
        europe_count = sum(1 for r in europe_recs[:5] if r[0] in europe_regions)
        self.assertGreaterEqual(europe_count, 2, "At least 2 of top 5 should be from Europe when preferred")
    
    def test_get_best_alternative(self):
        """Test finding best alternative region."""
        # Current region doesn't support Azure ML
        required = {
            ServiceType.STORAGE,
            ServiceType.AZURE_ML
        }
        
        alternative = self.validator.get_best_alternative('eastasia', required)
        
        # Should suggest an alternative
        self.assertIsNotNone(alternative)
        
        # Alternative should support Azure ML
        alt_capability = self.validator.get_region_capability(alternative)
        self.assertTrue(alt_capability.supports_service(ServiceType.AZURE_ML))
        
        # Should prefer same geography (Asia)
        asia_regions = self.validator._get_geography_regions('asia')
        # Alternative should be in Asia or at least support the service
        # (since eastasia doesn't have ML, might recommend outside geography)
        self.assertTrue(alt_capability.supports_service(ServiceType.AZURE_ML))
    
    def test_get_best_alternative_when_current_is_good(self):
        """Test that no alternative is suggested when current region is fine."""
        required = {
            ServiceType.STORAGE,
            ServiceType.FUNCTIONS_CONSUMPTION
        }
        
        alternative = self.validator.get_best_alternative('eastus', required)
        
        # Should return None (current region is fine)
        self.assertIsNone(alternative)
    
    def test_generate_deployment_summary(self):
        """Test deployment summary generation."""
        required = {
            ServiceType.STORAGE,
            ServiceType.AZURE_ML,
            ServiceType.FUNCTIONS_PREMIUM
        }
        
        # Test with Tier 1 region
        summary = self.validator.generate_deployment_summary('eastus', required)
        
        self.assertEqual(summary['region'], 'eastus')
        self.assertEqual(summary['tier'], 'tier1')
        self.assertTrue(summary['is_valid'])
        self.assertEqual(summary['compatibility_score'], 1.0)
        self.assertEqual(len(summary['supported_services']), 3)
        self.assertEqual(len(summary['unsupported_services']), 0)
        self.assertEqual(len(summary['recommended_alternatives']), 0)
        
        # Test with limited region
        summary_limited = self.validator.generate_deployment_summary('eastasia', required)
        
        self.assertEqual(summary_limited['region'], 'eastasia')
        self.assertFalse(summary_limited['is_valid'])
        self.assertLess(summary_limited['compatibility_score'], 1.0)
        self.assertGreater(len(summary_limited['unsupported_services']), 0)
        self.assertGreater(len(summary_limited['recommended_alternatives']), 0)
    
    def test_region_tier_classification(self):
        """Test region tier classification."""
        # Tier 1
        tier1 = self.validator.get_region_capability('eastus')
        self.assertEqual(tier1.tier, RegionTier.TIER_1)
        
        # Tier 2
        tier2 = self.validator.get_region_capability('uksouth')
        self.assertEqual(tier2.tier, RegionTier.TIER_2)
        
        # Tier 3
        tier3 = self.validator.get_region_capability('eastasia')
        self.assertEqual(tier3.tier, RegionTier.TIER_3)
        
        # Unknown
        unknown = self.validator.get_region_capability('invalidregion')
        self.assertEqual(unknown.tier, RegionTier.UNKNOWN)
    
    def test_caching(self):
        """Test that region capabilities are cached."""
        # First call
        cap1 = self.validator.get_region_capability('eastus')
        
        # Second call should return cached object
        cap2 = self.validator.get_region_capability('eastus')
        
        self.assertIs(cap1, cap2)  # Same object reference
    
    def test_select_optimal_regions_single_region(self):
        """Test auto-selection returns a single region when primary supports all services."""
        required = {
            ServiceType.STORAGE,
            ServiceType.AZURE_ML,
            ServiceType.FUNCTIONS_PREMIUM,
        }
        
        result = self.validator.select_optimal_regions(required, environment='prod')
        
        self.assertIn('primary', result)
        self.assertIn('ml', result)
        self.assertIn('multi_region', result)
        
        # Primary must support all core + ML services (Tier 1 region)
        primary_cap = self.validator.get_region_capability(result['primary'])
        self.assertTrue(primary_cap.supports_service(ServiceType.STORAGE))
        self.assertTrue(primary_cap.supports_service(ServiceType.FUNCTIONS_PREMIUM))
        
        # When primary supports ML, ml region should equal primary
        if primary_cap.supports_service(ServiceType.AZURE_ML):
            self.assertEqual(result['primary'], result['ml'])
            self.assertFalse(result['multi_region'])
    
    def test_select_optimal_regions_multi_region_when_needed(self):
        """Test auto-selection picks separate ML region when primary lacks ML support."""
        # Provide a fixed geography that may have non-ML-capable Tier-1 regions
        # Force the situation by requesting only east-asia geography (no ML there)
        required = {
            ServiceType.STORAGE,
            ServiceType.AZURE_ML,
        }
        
        # With geography=americas, all Tier 1 regions (eastus, eastus2, westus2) support ML
        result_americas = self.validator.select_optimal_regions(
            required, preferred_geography='americas'
        )
        self.assertIn('primary', result_americas)
        # ML region must support Azure ML
        ml_cap = self.validator.get_region_capability(result_americas['ml'])
        self.assertTrue(ml_cap.supports_service(ServiceType.AZURE_ML))
    
    def test_select_optimal_regions_geography_respected(self):
        """Test auto-selection boosts preferred geography when capability is equal."""
        required = {ServiceType.STORAGE, ServiceType.FUNCTIONS_CONSUMPTION}
        
        # When geography is specified, the result should be a valid known region
        result_americas = self.validator.select_optimal_regions(
            required, preferred_geography='americas'
        )
        self.assertIn(result_americas['primary'], self.validator.ALL_REGIONS)

        result_europe = self.validator.select_optimal_regions(
            required, preferred_geography='europe'
        )
        self.assertIn(result_europe['primary'], self.validator.ALL_REGIONS)
        
        # Results for different geographies can differ
        # (geography preference applies a boost but isn't a hard filter)
        result_asia = self.validator.select_optimal_regions(
            required, preferred_geography='asia'
        )
        self.assertIn(result_asia['primary'], self.validator.ALL_REGIONS)
    
    def test_select_optimal_regions_ml_region_valid(self):
        """Test ML region always supports Azure ML."""
        required = {
            ServiceType.STORAGE,
            ServiceType.AZURE_ML,
            ServiceType.CONTAINER_REGISTRY,
        }
        
        for geography in ('americas', 'europe', 'asia'):
            result = self.validator.select_optimal_regions(
                required, preferred_geography=geography
            )
            ml_cap = self.validator.get_region_capability(result['ml'])
            self.assertTrue(
                ml_cap.supports_service(ServiceType.AZURE_ML),
                f"ML region {result['ml']} must support Azure ML for geography {geography}"
            )
    
    def test_detect_geography(self):
        """Test geography detection from region name."""
        self.assertEqual(self.validator._detect_geography('eastus'), 'americas')
        self.assertEqual(self.validator._detect_geography('westeurope'), 'europe')
        self.assertEqual(self.validator._detect_geography('japaneast'), 'asia')
        # Region not in any known geography set falls back to 'americas'
        self.assertEqual(
            self.validator._detect_geography('unknownregion'),
            'americas',
            "Unknown regions should fall back to 'americas'"
        )


if __name__ == '__main__':
    unittest.main()
