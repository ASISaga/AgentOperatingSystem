"""AOS CLI — command-line interface for common AOS operations.

Usage::

    aos health --endpoint https://my-aos.azurewebsites.net
    aos agents list --endpoint https://my-aos.azurewebsites.net
    aos register --app business-infinity --endpoint https://my-aos.azurewebsites.net
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from typing import List, Optional


def _get_client(endpoint: str):
    """Create an AOSClient for the given endpoint."""
    from aos_client.client import AOSClient
    return AOSClient(endpoint=endpoint)


async def _health(endpoint: str) -> None:
    """Check AOS health."""
    async with _get_client(endpoint) as client:
        result = await client.health_check()
    print(json.dumps(result, indent=2, default=str))


async def _agents_list(endpoint: str, agent_type: Optional[str] = None) -> None:
    """List agents from the catalog."""
    async with _get_client(endpoint) as client:
        agents = await client.list_agents(agent_type=agent_type)
    for agent in agents:
        print(f"  {agent.agent_id:20s}  {agent.agent_type:20s}  {agent.purpose}")
    print(f"\n{len(agents)} agent(s) found.")


async def _register(endpoint: str, app_name: str, workflows: List[str]) -> None:
    """Register an application with AOS."""
    from aos_client.registration import AOSRegistration
    reg = AOSRegistration(endpoint=endpoint)
    result = await reg.register(app_name=app_name, workflows=workflows)
    print(json.dumps(result if isinstance(result, dict) else {"status": "registered"}, indent=2, default=str))


def main(argv: Optional[List[str]] = None) -> None:
    """Entry point for the ``aos`` CLI."""
    parser = argparse.ArgumentParser(prog="aos", description="AOS Client SDK CLI")
    parser.add_argument("--endpoint", default="http://localhost:7071", help="AOS endpoint URL")
    subparsers = parser.add_subparsers(dest="command")

    # health
    subparsers.add_parser("health", help="Check AOS health")

    # agents
    agents_parser = subparsers.add_parser("agents", help="Agent catalog operations")
    agents_sub = agents_parser.add_subparsers(dest="agents_action")
    list_parser = agents_sub.add_parser("list", help="List agents")
    list_parser.add_argument("--type", dest="agent_type", default=None, help="Filter by agent type")

    # register
    reg_parser = subparsers.add_parser("register", help="Register an application")
    reg_parser.add_argument("--app", required=True, help="Application name")
    reg_parser.add_argument("--workflows", default="", help="Comma-separated workflow names")

    args = parser.parse_args(argv)

    if args.command == "health":
        asyncio.run(_health(args.endpoint))
    elif args.command == "agents":
        if args.agents_action == "list":
            asyncio.run(_agents_list(args.endpoint, agent_type=args.agent_type))
        else:
            agents_parser.print_help()
    elif args.command == "register":
        workflows = [w.strip() for w in args.workflows.split(",") if w.strip()]
        asyncio.run(_register(args.endpoint, args.app, workflows))
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
