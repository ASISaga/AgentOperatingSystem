"""
In contrast to Goal Driven Agents, the Perpetual Agent is an asynchronous agent that is always active, and triggered periodically
to perform tasks requiring constant monitoring or regular intervals. It operates continuously, enhancing efficiency,
and responsiveness without manual intervention, thus enhancing efficiency and responsiveness in dynamic environments.
The Perpetual Agent is designed to be autonomous, self-sufficient, and capable of executing tasks without human intervention."""

# Run a single agent in a RoundRobinGroupChat team configuration with a TextMessageTermination condition.
# This is useful for running the AssistantAgent in a loop until a termination condition is met.
# The task is to increment a number until it reaches 10 using a tool.
# The agent will keep calling the tool until the number reaches 10, and then it will return a final TextMessage which will stop the run.

from config import model

from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient

class PerpetualAgent(AssistantAgent):
    def __init__(self, tools, system_message):
        super().__init__(name="PerpetualAgent", model_client=self.model_client, tools=tools, system_message=system_message)

    @staticmethod
    def increment_number(number: int) -> int:
        """Increment a number by 1."""
        return number + 1

    # Initialize the model client.
    model_client = OpenAIChatCompletionClient(
        model=model,
        # api_key="sk-...", # Optional if you have an OPENAI_API_KEY env variable set.
        # Disable parallel tool calls for this example.
        parallel_tool_calls=False,  # type: ignore
    )

    tools=[increment_number]  # Register the tool.
    system_message="You are a helpful AI assistant, use the tool to increment the number."

