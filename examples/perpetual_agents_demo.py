"""
Standalone Demo: Perpetual Agent vs Task-Based Framework

This demo shows the conceptual difference between:
1. Traditional AI Frameworks (Task-Based Sessions)
2. Agent Operating System (Perpetual Persistence)

No external dependencies required - pure demonstration.
"""

import asyncio
from datetime import datetime
from typing import Dict, Any, List


# ============================================================================
# PART 1: Traditional Framework (Task-Based Sessions)
# ============================================================================

class TaskBasedAgent:
    """
    Traditional AI Agent - Task-based session model.
    
    - Created for a specific task
    - Processes the task
    - Terminates when done
    - State is lost
    """
    
    def __init__(self, task_id: str):
        self.task_id = task_id
        self.created_at = datetime.utcnow()
        print(f"  ➤ TaskBasedAgent created for task: {task_id}")
    
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single task and terminate."""
        print(f"  ➤ Processing task: {self.task_id}")
        result = {"task": self.task_id, "status": "completed", "data": data}
        print(f"  ➤ Task {self.task_id} completed")
        print(f"  ➤ Agent terminating... (state will be lost)")
        # Agent terminates here - all context lost
        return result


def demonstrate_task_based_framework():
    """
    Traditional Framework: Must create new agent for each task.
    No memory between tasks.
    """
    print("\n" + "=" * 80)
    print("TRADITIONAL AI FRAMEWORK (Task-Based Sessions)")
    print("=" * 80)
    print()
    
    print("Day 1 - Morning Task:")
    agent1 = TaskBasedAgent("morning_decision")
    result1 = agent1.process({"decision": "hire_engineer"})
    print(f"  Result: {result1}")
    print(f"  ❌ Agent terminated - state lost\n")
    
    print("Day 1 - Afternoon Task:")
    print("  ⚠️  Must create NEW agent (no memory of morning task)")
    agent2 = TaskBasedAgent("afternoon_decision")  # New agent, no memory
    result2 = agent2.process({"decision": "approve_budget"})
    print(f"  Result: {result2}")
    print(f"  ❌ Agent terminated - state lost\n")
    
    print("Day 2 - New Task:")
    print("  ⚠️  Must create YET ANOTHER agent (no memory of Day 1)")
    agent3 = TaskBasedAgent("day2_decision")  # New agent, no history
    result3 = agent3.process({"decision": "launch_product"})
    print(f"  Result: {result3}")
    print(f"  ❌ Agent terminated - state lost\n")
    
    print("Problems with Task-Based Model:")
    print("  ❌ Created 3 separate agents for 3 tasks")
    print("  ❌ No state preservation between tasks")
    print("  ❌ No memory or context accumulation")
    print("  ❌ Manual agent creation for each task")
    print("  ❌ Cannot build knowledge over time")


# ============================================================================
# PART 2: Agent Operating System (Perpetual Persistence)
# ============================================================================

class AlwaysOnAgentSimple:
    """
    AOS Agent - Always-on persistent model.
    
    - Registered once and runs forever
    - Sleeps when idle, awakens on events
    - Preserves state across all events
    - Builds knowledge over time
    """
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.created_at = datetime.utcnow()
        self.is_running = False
        self.sleep_mode = True
        
        # Persistent state - preserved across ALL events
        self.event_count = 0
        self.event_history: List[Dict[str, Any]] = []
        self.context: Dict[str, Any] = {}
        self.wake_count = 0
        
        print(f"  ✅ AlwaysOnAgent '{agent_id}' created (will run indefinitely)")
    
    def start(self):
        """Start the agent - it will run indefinitely."""
        self.is_running = True
        print(f"  ✅ Agent '{self.agent_id}' started - now running FOREVER")
        print(f"  ⏰ Agent entering sleep mode (will awaken on events)")
    
    async def handle_event(self, event: Dict[str, Any]):
        """
        Handle an event.
        
        The agent awakens, processes the event, updates its persistent
        state, then returns to sleep.
        """
        # Awaken from sleep
        if self.sleep_mode:
            self.wake_count += 1
            print(f"  ⚡ Agent '{self.agent_id}' awakened (wake #{self.wake_count})")
            self.sleep_mode = False
        
        # Process event
        print(f"  ⚙️  Processing event: {event.get('type')}")
        self.event_count += 1
        
        # Update persistent state
        self.event_history.append({
            "timestamp": datetime.utcnow().isoformat(),
            "event": event,
            "event_number": self.event_count
        })
        
        # Update context based on event
        if "decision" in event.get("data", {}):
            self.context.setdefault("decisions_made", []).append(
                event["data"]["decision"]
            )
        
        result = {
            "agent_id": self.agent_id,
            "event_number": self.event_count,
            "total_events": len(self.event_history),
            "status": "success"
        }
        
        print(f"  ✅ Event processed (total events: {self.event_count})")
        
        # Return to sleep
        self.sleep_mode = True
        print(f"  😴 Agent returning to sleep (state preserved)")
        
        return result
    
    def get_state(self) -> Dict[str, Any]:
        """Get current persistent state."""
        return {
            "agent_id": self.agent_id,
            "is_running": self.is_running,
            "event_count": self.event_count,
            "wake_count": self.wake_count,
            "context": self.context,
            "created_at": self.created_at.isoformat(),
            "history_length": len(self.event_history)
        }


async def demonstrate_perpetual_agent():
    """
    Agent Operating System: Register once, runs forever.
    Full memory across all events.
    """
    print("\n" + "=" * 80)
    print("AGENT OPERATING SYSTEM (Perpetual Persistence)")
    print("=" * 80)
    print()
    
    print("Initialize Agent Operating System:")
    agent = AlwaysOnAgentSimple("ceo")
    agent.start()
    print()
    
    print("Day 1 - Morning Event:")
    event1 = {"type": "DecisionRequest", "data": {"decision": "hire_engineer"}}
    await agent.handle_event(event1)
    state1 = agent.get_state()
    print(f"  📊 State: {state1['event_count']} events, {state1['wake_count']} awakenings")
    print(f"  ✅ Agent STILL RUNNING (state preserved)\n")
    
    print("Day 1 - Afternoon Event:")
    print("  ℹ️  SAME agent (remembers morning event)")
    event2 = {"type": "DecisionRequest", "data": {"decision": "approve_budget"}}
    await agent.handle_event(event2)
    state2 = agent.get_state()
    print(f"  📊 State: {state2['event_count']} events, {state2['wake_count']} awakenings")
    print(f"  💾 Context: {state2['context']}")
    print(f"  ✅ Agent STILL RUNNING (full history maintained)\n")
    
    print("Day 2 - New Event:")
    print("  ℹ️  SAME agent (remembers ALL of Day 1)")
    event3 = {"type": "DecisionRequest", "data": {"decision": "launch_product"}}
    await agent.handle_event(event3)
    state3 = agent.get_state()
    print(f"  📊 State: {state3['event_count']} events, {state3['wake_count']} awakenings")
    print(f"  💾 Context: {state3['context']}")
    print(f"  ✅ Agent STILL RUNNING (complete history from Day 1)\n")
    
    print("Week Later - Another Event:")
    print("  ℹ️  SAME agent (remembers entire week)")
    event4 = {"type": "DecisionRequest", "data": {"decision": "expand_market"}}
    await agent.handle_event(event4)
    state4 = agent.get_state()
    print(f"  📊 State: {state4['event_count']} events, {state4['wake_count']} awakenings")
    print(f"  💾 All Decisions: {state4['context']['decisions_made']}")
    print(f"  ✅ Agent STILL RUNNING (never terminated)\n")
    
    print("Benefits of Perpetual Model:")
    print("  ✅ ONE agent for ALL events (registered once)")
    print("  ✅ Complete state preservation across events")
    print("  ✅ Full memory and context accumulation")
    print("  ✅ Event-driven awakening (no manual management)")
    print("  ✅ Builds knowledge continuously over time")
    print()
    
    print(f"Final Agent State:")
    final_state = agent.get_state()
    for key, value in final_state.items():
        if key != 'context':
            print(f"  {key}: {value}")
    print(f"  decisions_made: {final_state['context']['decisions_made']}")


# ============================================================================
# COMPARISON
# ============================================================================

def show_comparison():
    """Side-by-side comparison."""
    print("\n" + "=" * 80)
    print("COMPARISON: Task-Based vs Perpetual")
    print("=" * 80)
    print()
    
    comparison = [
        ("Paradigm", "Task-Based Sessions", "Perpetual Persistence"),
        ("Agent Creation", "New agent per task", "Register once, run forever"),
        ("Lifecycle", "Start → Work → Stop", "Register → Run indefinitely"),
        ("State", "Lost after completion", "Preserved indefinitely"),
        ("Memory", "Current task only", "Full history"),
        ("Activation", "Manual start/stop", "Event-driven awakening"),
        ("Context", "Isolated per task", "Continuous accumulation"),
        ("Resource Usage", "Create/destroy overhead", "Sleep when idle"),
        ("Use Case", "Single tasks", "Continuous operations"),
    ]
    
    print(f"{'Aspect':<20} {'Traditional Framework':<30} {'Agent OS':<30}")
    print("-" * 80)
    for aspect, traditional, aos in comparison:
        print(f"{aspect:<20} {traditional:<30} {aos:<30}")
    
    print()
    print("CODE COMPARISON:")
    print()
    print("Traditional Framework:")
    print("  for task in tasks:")
    print("      agent = create_agent()  # New agent")
    print("      agent.process(task)")
    print("      # Agent terminates, state lost")
    print()
    print("Agent Operating System:")
    print("  agent = AlwaysOnAgent('ceo')")
    print("  agent.start()  # Runs forever")
    print("  # Events trigger automatic awakening")
    print("  # State persists across ALL events")
    print("  # Agent never stops unless explicitly deregistered")


# ============================================================================
# MAIN
# ============================================================================

async def main():
    """Run all demonstrations."""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "  AGENT OPERATING SYSTEM vs TRADITIONAL AI FRAMEWORKS".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("║" + "  Demonstrating the Core USP: Perpetual Persistence".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "=" * 78 + "╝")
    
    # Part 1: Traditional framework
    demonstrate_task_based_framework()
    
    # Part 2: Always-on agent
    await demonstrate_perpetual_agent()
    
    # Part 3: Comparison
    show_comparison()
    
    print("\n" + "=" * 80)
    print("CONCLUSION")
    print("=" * 80)
    print()
    print("The Agent Operating System differentiates itself through PERSISTENCE:")
    print()
    print("• Traditional frameworks: Temporary task executors")
    print("• Agent OS: Permanent entities with continuous operations")
    print()
    print("This makes AOS a true 'operating system' for agents, not just")
    print("a task orchestration framework.")
    print()


if __name__ == "__main__":
    asyncio.run(main())
