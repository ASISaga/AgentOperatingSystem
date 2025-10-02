from PerpetualAgent import PerpetualAgent
from PurposeDrivenAgent.CoderAgent import CoderAgent

from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import TextMessageTermination

# Termination condition that stops the task if the agent responds with a text message.
termination_condition = TextMessageTermination("looped_assistant")

# Create a tool agent that uses the increment_number function.
perpetual_agent = PerpetualAgent()

coder_agent = CoderAgent()

# Create a team with the looped assistant agent and the termination condition.
team = RoundRobinGroupChat(
    [perpetual_agent, coder_agent],
    termination_condition=termination_condition,
)

# Run the team with a task and print the messages to the console.
async for message in team.run_stream(task="Increment the number 5 to 10."):  # type: ignore
    print(type(message).__name__, message)
