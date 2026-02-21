"""
BaseExecutor for agent_framework-based executors.
Provides a stable abstraction for all AOS executors.

In agent-framework >= 1.0.0rc1, use WorkflowBuilder with add_edge()/add_chain()
to compose executors into workflows.
"""
from agent_framework import Executor, WorkflowContext as _WorkflowContext, handler as _handler

# Re-export for downstream executors
WorkflowContext = _WorkflowContext
handler = _handler

class BaseExecutor(Executor):
    """
    Base class for all agent_framework-based executors in AOS.
    Inherit from this class to ensure consistent interface and future-proofing.
    """
    def __init__(self, id: str):
        super().__init__(id)

    @handler
    async def handle(self, intent: dict, ctx: WorkflowContext[dict]):
        """Default handler (should be overridden by subclasses)"""
        await ctx.yield_output({"error": f"Handler not implemented in {self.__class__.__name__}"})
