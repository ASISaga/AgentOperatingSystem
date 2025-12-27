"""
Example: Perpetual Agent Operating System

This example demonstrates the key difference between Agent Operating System
and traditional AI frameworks:

TRADITIONAL AI FRAMEWORKS (Task-Based):
- Start agent for a specific task
- Agent processes the task
- Agent completes and terminates
- State is lost unless explicitly saved
- Must restart agent for each new task

AGENT OPERATING SYSTEM (Perpetual):
- Register agent once
- Agent runs indefinitely
- Agent responds to events automatically
- State persists across all interactions
- True "operating system" for agents

This example shows a C-suite of agents running continuously, responding
to business events as they occur.
"""

import asyncio
import sys
import os
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from AgentOperatingSystem.agents.perpetual import AlwaysOnAgent
from AgentOperatingSystem.agents.manager import UnifiedAgentManager


class CEOAgent(AlwaysOnAgent):
    """CEO Agent - Strategic decision making"""
    
    def __init__(self):
        super().__init__(
            agent_id="ceo",
            name="Chief Executive Officer",
            role="executive"
        )
        self.decisions_made = []
    
    async def handle_strategic_decision(self, event_data):
        """Handle strategic decisions"""
        decision = event_data.get("decision")
        print(f"[CEO] 🎯 Evaluating strategic decision: {decision}")
        
        # CEO maintains context of all decisions
        self.decisions_made.append({
            "decision": decision,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        await self.update_context({
            "total_decisions": len(self.decisions_made),
            "last_decision": decision
        })
        
        return {"approved": True, "rationale": "Strategic alignment confirmed"}


class CFOAgent(AlwaysOnAgent):
    """CFO Agent - Financial oversight"""
    
    def __init__(self):
        super().__init__(
            agent_id="cfo",
            name="Chief Financial Officer",
            role="finance"
        )
        self.budget_requests = []
    
    async def handle_budget_request(self, event_data):
        """Handle budget requests"""
        amount = event_data.get("amount")
        department = event_data.get("department")
        
        print(f"[CFO] 💰 Reviewing budget request: ${amount:,} for {department}")
        
        # Track all budget requests
        self.budget_requests.append({
            "amount": amount,
            "department": department,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        total_allocated = sum(r["amount"] for r in self.budget_requests)
        await self.update_context({
            "total_allocated": total_allocated,
            "request_count": len(self.budget_requests)
        })
        
        return {"approved": amount < 100000, "total_allocated": total_allocated}


class CTOAgent(AlwaysOnAgent):
    """CTO Agent - Technology oversight"""
    
    def __init__(self):
        super().__init__(
            agent_id="cto",
            name="Chief Technology Officer",
            role="technology"
        )
        self.deployments = []
    
    async def handle_deployment(self, event_data):
        """Handle deployment approvals"""
        service = event_data.get("service")
        version = event_data.get("version")
        
        print(f"[CTO] 🚀 Reviewing deployment: {service} v{version}")
        
        # Track deployment history
        self.deployments.append({
            "service": service,
            "version": version,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        await self.update_context({
            "total_deployments": len(self.deployments),
            "last_deployment": service
        })
        
        return {"approved": True, "deployment_count": len(self.deployments)}


async def demonstrate_perpetual_agents():
    """
    Demonstrate the perpetual agent model.
    
    In this demo:
    1. Agents are registered once and run indefinitely
    2. Events are sent to agents as they occur
    3. Agents maintain state across all events
    4. Agents never terminate (unless explicitly stopped)
    """
    
    print("=" * 80)
    print("AGENT OPERATING SYSTEM - Perpetual Agent Demo")
    print("=" * 80)
    print()
    
    # Create the agent manager
    manager = UnifiedAgentManager()
    
    # Create C-suite agents
    print("📋 Creating C-suite agents...")
    ceo = CEOAgent()
    cfo = CFOAgent()
    cto = CTOAgent()
    
    # Set up event handlers
    await ceo.subscribe_to_event("StrategyDecision", ceo.handle_strategic_decision)
    await cfo.subscribe_to_event("BudgetRequest", cfo.handle_budget_request)
    await cto.subscribe_to_event("Deployment", cto.handle_deployment)
    
    # Register agents as perpetual
    print("🔄 Registering agents in perpetual mode...")
    await manager.register_agent(ceo, perpetual=True)
    await manager.register_agent(cfo, perpetual=True)
    await manager.register_agent(cto, perpetual=True)
    
    print()
    print("✅ Agents registered and running indefinitely!")
    print()
    
    # Show statistics
    stats = manager.get_agent_statistics()
    print(f"📊 Agent Statistics:")
    print(f"   Total Agents: {stats['total_agents']}")
    print(f"   Perpetual Agents: {stats['perpetual_agents']}")
    print(f"   Perpetual Percentage: {stats['perpetual_percentage']:.0f}%")
    print()
    
    # Simulate business events over time
    print("🎬 Simulating business events...")
    print("-" * 80)
    print()
    
    # Day 1: Strategic planning
    print("📅 DAY 1: Strategic Planning")
    await ceo.handle_message({
        "type": "StrategyDecision",
        "data": {"decision": "Expand to European market"}
    })
    await ceo.handle_message({
        "type": "StrategyDecision",
        "data": {"decision": "Launch new product line"}
    })
    print()
    
    # Day 2: Budget allocation
    print("📅 DAY 2: Budget Allocation")
    await cfo.handle_message({
        "type": "BudgetRequest",
        "data": {"amount": 50000, "department": "Engineering"}
    })
    await cfo.handle_message({
        "type": "BudgetRequest",
        "data": {"amount": 75000, "department": "Marketing"}
    })
    await cfo.handle_message({
        "type": "BudgetRequest",
        "data": {"amount": 25000, "department": "HR"}
    })
    print()
    
    # Day 3: Technology deployments
    print("📅 DAY 3: Technology Deployments")
    await cto.handle_message({
        "type": "Deployment",
        "data": {"service": "api-gateway", "version": "2.1.0"}
    })
    await cto.handle_message({
        "type": "Deployment",
        "data": {"service": "auth-service", "version": "1.5.0"}
    })
    print()
    
    # Day 4: Mixed activities
    print("📅 DAY 4: Mixed Activities")
    await ceo.handle_message({
        "type": "StrategyDecision",
        "data": {"decision": "Acquire competitor startup"}
    })
    await cfo.handle_message({
        "type": "BudgetRequest",
        "data": {"amount": 150000, "department": "Acquisitions"}
    })
    await cto.handle_message({
        "type": "Deployment",
        "data": {"service": "analytics-platform", "version": "3.0.0"}
    })
    print()
    
    print("-" * 80)
    print()
    
    # Show persistent state
    print("💾 PERSISTENT STATE AFTER 4 DAYS:")
    print()
    
    ceo_state = await ceo.get_persistent_state()
    print(f"👔 CEO:")
    print(f"   Total Events Processed: {ceo_state['total_events_processed']}")
    print(f"   Total Decisions: {ceo_state['context'].get('total_decisions', 0)}")
    print(f"   Last Decision: {ceo_state['context'].get('last_decision', 'N/A')}")
    print(f"   Wake Count: {ceo_state['wake_count']}")
    print(f"   Still Running: {ceo_state['is_running']}")
    print()
    
    cfo_state = await cfo.get_persistent_state()
    print(f"💰 CFO:")
    print(f"   Total Events Processed: {cfo_state['total_events_processed']}")
    print(f"   Budget Requests: {cfo_state['context'].get('request_count', 0)}")
    print(f"   Total Allocated: ${cfo_state['context'].get('total_allocated', 0):,}")
    print(f"   Wake Count: {cfo_state['wake_count']}")
    print(f"   Still Running: {cfo_state['is_running']}")
    print()
    
    cto_state = await cto.get_persistent_state()
    print(f"🚀 CTO:")
    print(f"   Total Events Processed: {cto_state['total_events_processed']}")
    print(f"   Total Deployments: {cto_state['context'].get('total_deployments', 0)}")
    print(f"   Last Deployment: {cto_state['context'].get('last_deployment', 'N/A')}")
    print(f"   Wake Count: {cto_state['wake_count']}")
    print(f"   Still Running: {cto_state['is_running']}")
    print()
    
    # Health check
    print("🏥 HEALTH CHECK:")
    health = await manager.health_check_all()
    for agent_id, status in health.items():
        print(f"   {agent_id}: {status['state']} ({status['operational_mode']})")
    print()
    
    print("=" * 80)
    print("KEY OBSERVATIONS:")
    print("=" * 80)
    print()
    print("1. ✅ Agents were registered ONCE and ran continuously")
    print("2. ✅ Agents responded to events automatically (no manual start/stop)")
    print("3. ✅ Agent state persisted across all events and days")
    print("4. ✅ Agents are STILL RUNNING (not terminated)")
    print("5. ✅ Each agent maintains its own context and history")
    print()
    print("This is the Agent Operating System model: Perpetual, Event-Driven, Persistent")
    print()
    print("CONTRAST WITH TRADITIONAL FRAMEWORKS:")
    print("- Traditional: Start agent → Process task → Stop agent → Lose state")
    print("- AOS: Register agent → Runs forever → Responds to events → Keeps state")
    print()
    
    # Clean up
    print("🧹 Shutting down agents...")
    await manager.deregister_agent("ceo")
    await manager.deregister_agent("cfo")
    await manager.deregister_agent("cto")
    
    print("✅ Demo complete!")


async def demonstrate_traditional_vs_aos():
    """
    Side-by-side comparison of traditional vs AOS approach.
    """
    print("\n" + "=" * 80)
    print("COMPARISON: Traditional Framework vs Agent Operating System")
    print("=" * 80)
    print()
    
    print("TRADITIONAL FRAMEWORK (Task-Based Session):")
    print("-" * 80)
    print("```python")
    print("# Task 1")
    print("agent = TaskBasedAgent()")
    print("result1 = agent.process('task-1')")
    print("# Agent terminates, state lost")
    print()
    print("# Task 2 - Must recreate agent")
    print("agent = TaskBasedAgent()  # No memory of task-1")
    print("result2 = agent.process('task-2')")
    print("# Agent terminates again")
    print("```")
    print()
    print("Problems:")
    print("❌ Must recreate agent for each task")
    print("❌ No state persistence")
    print("❌ No event-driven behavior")
    print("❌ Manual lifecycle management")
    print()
    
    print("AGENT OPERATING SYSTEM (Perpetual):")
    print("-" * 80)
    print("```python")
    print("# Register once")
    print("agent = AlwaysOnAgent(agent_id='ceo')")
    print("manager.register_agent(agent, perpetual=True)")
    print()
    print("# Agent runs indefinitely, responds to events")
    print("# Day 1")
    print("await agent.handle_message(event1)  # State preserved")
    print("# Day 2")
    print("await agent.handle_message(event2)  # Remembers Day 1")
    print("# Day 365")
    print("await agent.handle_message(event365)  # Full history")
    print("```")
    print()
    print("Benefits:")
    print("✅ Register once, run forever")
    print("✅ Complete state persistence")
    print("✅ Event-driven awakening")
    print("✅ No manual lifecycle management")
    print("✅ True 'operating system' paradigm")
    print()


if __name__ == "__main__":
    # Run the demonstrations
    asyncio.run(demonstrate_perpetual_agents())
    asyncio.run(demonstrate_traditional_vs_aos())
