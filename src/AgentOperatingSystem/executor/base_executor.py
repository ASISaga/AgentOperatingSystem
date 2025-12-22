"""
BaseExecutor for agent_framework-based executors.
Provides a stable abstraction for all AOS and BusinessInfinity executors.

Note: In agent-framework >= 1.0.0b251218, use WorkflowBuilder.register_executor()
or WorkflowBuilder.register_agent() instead of the deprecated add_executor() method.
"""
from agent_framework import Executor, WorkflowContext as _WorkflowContext, handler as _handler

# Re-export for downstream executors
WorkflowContext = _WorkflowContext
handler = _handler

class BaseExecutor(Executor):
    """
    Base class for all agent_framework-based executors in AOS and BusinessInfinity.
    Inherit from this class to ensure consistent interface and future-proofing.
    """
    def __init__(self, name: str):
        super().__init__(name)
        # Add any shared initialization logic here

    # Optionally, provide a default handler (can be overridden)

    @handler
    async def handle(self, intent: dict, ctx: WorkflowContext[dict]):
        """Default handler (should be overridden by subclasses)"""
        await ctx.yield_output({"error": f"Handler not implemented in {self.__class__.__name__}"})
