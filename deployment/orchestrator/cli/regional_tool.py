#!/usr/bin/env python3
"""
Regional Capability CLI Tool

Provides command-line interface for regional capability queries and recommendations.
"""

import argparse
import sys
import json
from pathlib import Path

# Add parent directory to path to import regional_validator
sys.path.insert(0, str(Path(__file__).parent.parent))

from validators.regional_validator import RegionalValidator, ServiceType


def parse_services(service_strings):
    """Parse service type strings into ServiceType set."""
    services = set()
    service_map = {
        'storage': ServiceType.STORAGE,
        'keyvault': ServiceType.KEY_VAULT,
        'functions': ServiceType.FUNCTIONS_CONSUMPTION,
        'functions-premium': ServiceType.FUNCTIONS_PREMIUM,
        'servicebus': ServiceType.SERVICE_BUS_STANDARD,
        'servicebus-premium': ServiceType.SERVICE_BUS_PREMIUM,
        'appinsights': ServiceType.APP_INSIGHTS,
        'loganalytics': ServiceType.LOG_ANALYTICS,
        'azureml': ServiceType.AZURE_ML,
        'acr': ServiceType.CONTAINER_REGISTRY,
        'identity': ServiceType.MANAGED_IDENTITY,
    }
    
    for s in service_strings:
        s_lower = s.lower()
        if s_lower in service_map:
            services.add(service_map[s_lower])
        else:
            print(f"Warning: Unknown service '{s}', skipping", file=sys.stderr)
    
    return services


def cmd_validate(args):
    """Validate a region for required services."""
    validator = RegionalValidator()
    services = parse_services(args.services)
    
    if not services:
        print("Error: No valid services specified", file=sys.stderr)
        return 1
    
    is_valid, warnings = validator.validate_region(args.region, services)
    
    if args.json:
        result = {
            'region': args.region,
            'is_valid': is_valid,
            'warnings': warnings
        }
        print(json.dumps(result, indent=2))
    else:
        print(f"Region: {args.region}")
        print(f"Valid: {'✅ Yes' if is_valid else '❌ No'}")
        
        if warnings:
            print("\nWarnings:")
            for warning in warnings:
                print(f"  • {warning}")
        else:
            print("\n✅ No warnings - region fully supports all requested services")
    
    return 0 if is_valid else 1


def cmd_recommend(args):
    """Recommend regions for required services."""
    validator = RegionalValidator()
    services = parse_services(args.services)
    
    if not services:
        print("Error: No valid services specified", file=sys.stderr)
        return 1
    
    recommendations = validator.recommend_regions(
        services,
        preferred_geography=args.geography,
        limit=args.limit
    )
    
    if args.json:
        result = {
            'services': [s.value for s in services],
            'geography': args.geography,
            'recommendations': [
                {
                    'region': r,
                    'compatibility_score': round(score, 2),
                    'tier': tier.value
                }
                for r, score, tier in recommendations
            ]
        }
        print(json.dumps(result, indent=2))
    else:
        print(f"Services Required: {', '.join(s.value for s in services)}")
        if args.geography:
            print(f"Geographic Preference: {args.geography}")
        print(f"\nTop {len(recommendations)} Recommended Regions:\n")
        
        for i, (region, score, tier) in enumerate(recommendations, 1):
            tier_emoji = {'tier1': '🏆', 'tier2': '⭐', 'tier3': '✓', 'unknown': '❓'}
            score_pct = int(score * 100)
            print(f"{i}. {region:20} {tier_emoji[tier.value]} {tier.value:10} {score_pct}% compatible")
    
    return 0


def cmd_check(args):
    """Check capability of a specific region."""
    validator = RegionalValidator()
    capability = validator.get_region_capability(args.region)
    
    if args.json:
        result = {
            'region': capability.region,
            'tier': capability.tier.value,
            'available_services': [s.value for s in capability.available_services],
            'unavailable_services': [s.value for s in capability.unavailable_services]
        }
        print(json.dumps(result, indent=2))
    else:
        tier_names = {
            'tier1': 'Tier 1 (Full Capability)',
            'tier2': 'Tier 2 (Good Coverage)',
            'tier3': 'Tier 3 (Basic Coverage)',
            'unknown': 'Unknown Region'
        }
        
        print(f"Region: {args.region}")
        print(f"Tier: {tier_names[capability.tier.value]}\n")
        
        print(f"Available Services ({len(capability.available_services)}):")
        for service in sorted(capability.available_services, key=lambda s: s.value):
            print(f"  ✅ {service.value}")
        
        if capability.unavailable_services:
            print(f"\nUnavailable Services ({len(capability.unavailable_services)}):")
            for service in sorted(capability.unavailable_services, key=lambda s: s.value):
                print(f"  ❌ {service.value}")
    
    return 0


def cmd_summary(args):
    """Generate deployment summary for a region."""
    validator = RegionalValidator()
    services = parse_services(args.services)
    
    if not services:
        print("Error: No valid services specified", file=sys.stderr)
        return 1
    
    summary = validator.generate_deployment_summary(args.region, services)
    
    if args.json:
        print(json.dumps(summary, indent=2))
    else:
        print(f"Deployment Summary for {args.region}\n")
        print(f"Region Tier: {summary['tier']}")
        print(f"Compatibility Score: {int(summary['compatibility_score'] * 100)}%")
        print(f"Valid for Deployment: {'✅ Yes' if summary['is_valid'] else '❌ No'}\n")
        
        if summary['supported_services']:
            print(f"Supported Services ({len(summary['supported_services'])}):")
            for service in summary['supported_services']:
                print(f"  ✅ {service}")
        
        if summary['unsupported_services']:
            print(f"\nUnsupported Services ({len(summary['unsupported_services'])}):")
            for service in summary['unsupported_services']:
                print(f"  ❌ {service}")
        
        if summary['warnings']:
            print("\nWarnings:")
            for warning in summary['warnings']:
                print(f"  ⚠️  {warning}")
        
        if summary['recommended_alternatives']:
            print("\nRecommended Alternatives:")
            for i, alt in enumerate(summary['recommended_alternatives'], 1):
                print(f"  {i}. {alt['region']} ({alt['tier']}, {int(alt['score']*100)}% compatible)")
    
    return 0


def cmd_auto_select(args):
    """Automatically select optimal regions for deployment."""
    validator = RegionalValidator()

    # Default service sets per environment
    env_services = {
        'dev': ['storage', 'keyvault', 'functions', 'servicebus',
                'appinsights', 'loganalytics', 'identity'],
        'staging': ['storage', 'keyvault', 'functions', 'functions-premium',
                    'servicebus', 'appinsights', 'loganalytics', 'identity', 'azureml'],
        'prod': ['storage', 'keyvault', 'functions', 'functions-premium',
                 'servicebus', 'servicebus-premium', 'appinsights', 'loganalytics',
                 'identity', 'azureml', 'acr'],
    }

    service_list = list(args.services) if args.services else env_services.get(
        args.environment, env_services['dev'])
    services = parse_services(service_list)

    if not services:
        print("Error: No valid services specified", file=sys.stderr)
        return 1

    regions = validator.select_optimal_regions(
        services,
        environment=args.environment,
        preferred_geography=args.geography
    )

    env = args.environment
    primary_rg = f"aos-{env}-rg"
    ml_rg = f"aos-{env}-ml-rg" if regions['multi_region'] else primary_rg

    result = {
        'environment': env,
        'primary_region': regions['primary'],
        'ml_region': regions['ml'],
        'primary_resource_group': primary_rg,
        'ml_resource_group': ml_rg,
        'multi_region': regions['multi_region'],
        'geography': regions.get('geography', 'americas'),
    }

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Auto-Selected Regions for '{env}' environment:")
        print(f"  Primary Region     : {result['primary_region']}")
        print(f"  Azure ML Region    : {result['ml_region']}")
        print(f"  Primary RG         : {result['primary_resource_group']}")
        print(f"  ML Resource Group  : {result['ml_resource_group']}")
        if result['multi_region']:
            print(f"\n  ⚠️  Multi-region deployment:")
            print(f"     Core services → {result['primary_region']}")
            print(f"     Azure ML/ACR  → {result['ml_region']}")
        else:
            print(f"\n  ✅ Single-region deployment ({result['primary_region']})")

    return 0


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Azure Regional Capability Tool for AOS Deployment'
    )

    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # validate command
    validate_parser = subparsers.add_parser(
        'validate',
        help='Validate if a region supports required services'
    )
    validate_parser.add_argument('region', help='Azure region to validate')
    validate_parser.add_argument(
        'services',
        nargs='+',
        help='Required services (storage, azureml, functions-premium, etc.)'
    )
    validate_parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    # recommend command
    recommend_parser = subparsers.add_parser(
        'recommend',
        help='Recommend regions for required services'
    )
    recommend_parser.add_argument(
        'services',
        nargs='+',
        help='Required services (storage, azureml, functions-premium, etc.)'
    )
    recommend_parser.add_argument(
        '--geography',
        choices=['americas', 'europe', 'asia'],
        help='Preferred geography'
    )
    recommend_parser.add_argument(
        '--limit',
        type=int,
        default=5,
        help='Number of recommendations (default: 5)'
    )
    recommend_parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    # check command
    check_parser = subparsers.add_parser(
        'check',
        help='Check capabilities of a specific region'
    )
    check_parser.add_argument('region', help='Azure region to check')
    check_parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    # summary command
    summary_parser = subparsers.add_parser(
        'summary',
        help='Generate deployment summary for a region'
    )
    summary_parser.add_argument('region', help='Azure region')
    summary_parser.add_argument(
        'services',
        nargs='+',
        help='Required services'
    )
    summary_parser.add_argument('--json', action='store_true', help='Output as JSON')

    # auto-select command
    auto_select_parser = subparsers.add_parser(
        'auto-select',
        help='Automatically select optimal regions per service for an environment'
    )
    auto_select_parser.add_argument(
        '--environment',
        choices=['dev', 'staging', 'prod'],
        default='dev',
        help='Target environment (default: dev)'
    )
    auto_select_parser.add_argument(
        '--geography',
        choices=['americas', 'europe', 'asia'],
        help='Preferred geography'
    )
    auto_select_parser.add_argument(
        'services',
        nargs='*',
        help='Override services list (defaults to environment preset)'
    )
    auto_select_parser.add_argument('--json', action='store_true', help='Output as JSON')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Execute command
    command_map = {
        'validate': cmd_validate,
        'recommend': cmd_recommend,
        'check': cmd_check,
        'summary': cmd_summary,
        'auto-select': cmd_auto_select,
    }

    return command_map[args.command](args)


if __name__ == '__main__':
    sys.exit(main())
