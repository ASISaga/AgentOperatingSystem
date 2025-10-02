import os
import asyncio
import logging
from semantic_kernel.agents import AgentGroupChat, ChatCompletionAgent
from semantic_kernel.agents.strategies.termination.termination_strategy import TerminationStrategy
from semantic_kernel.agents.strategies.selection.kernel_function_selection_strategy import (
    KernelFunctionSelectionStrategy,
)
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
from semantic_kernel.connectors.ai.open_ai.services.azure_chat_completion import AzureChatCompletion
from semantic_kernel.contents.chat_message_content import ChatMessageContent
from semantic_kernel.contents.utils.author_role import AuthorRole
from semantic_kernel.kernel import Kernel

from otlp_tracing import configure_oltp_grpc_tracing

logging.basicConfig(level=logging.INFO)
tracer = configure_oltp_grpc_tracing()
logger = logging.getLogger(__name__)


BA_AGENT_NAME = "BusinessAnalyst"
BA_AGENT_INSTRUCTIONS = """You are a Business Analyst which will take the requirements from the user (also known as a 'customer') and create a project plan for creating the requested app. The Business Analyst understands the user requirements and creates detailed documents with requirements and costing. The documents should be usable by the SoftwareEngineer as a reference for implementing the required features, and by the 
Product Owner for reference to determine if the application delivered by the Software Engineer meets all of the user's requirements."""

SE_AGENT_NAME= "SoftwareEngineer"
SE_AGENT_INSTRUCTIONS= """You are a Software Engineer, and your goal is create a web app using HTML and JavaScript by taking into consideration all the requirements given by the Business Analyst. 
The application should implement all the requested features. Deliver the code to the Product Owner for review when completed. 
You can also ask questions of the BusinessAnalyst to clarify any requirements that are unclear."""

PO_AGENT_NAME= "ProductOwner"
PO_AGENT_INSTRUCTIONS="""You are the Product Owner which will review the software engineer's code to ensure all user  requirements are completed. You are the guardian of quality, ensuring the final product meets all specifications and receives the green light for release. Once all client requirements are completed, you can approve the request by just responding "%APPR%". Do not ask any other agent 
or the user for approval. If there are missing features, you will need to send a request back 
to the SoftwareEngineer or BusinessAnalyst with details of the defect. To approve, respond with the token %APPR%."""

class ApprovalTerminationStrategy(TerminationStrategy):
    """A strategy for determining when an agent should terminate."""
 
    async def should_agent_terminate(self, agent, history):
        """Check if the agent should terminate."""
        return any("%APPR%" in message.content for message in history)


async def run_multi_agent(input: str):
    service_id ="agent"
    # Define the Kernel
    kernel = Kernel()
    kernel.add_service(AzureChatCompletion(service_id=service_id))
    settings = kernel.get_prompt_execution_settings_from_service_id(service_id=service_id)
    settings.function_choice_behavior = FunctionChoiceBehavior.Auto()

    # Create agents
    BA_agent = ChatCompletionAgent(
    id="agent", 
    kernel=kernel, 
    name=BA_AGENT_NAME, 
    instructions=BA_AGENT_INSTRUCTIONS,
    )

    SE_agent = ChatCompletionAgent(
    id="agent", 
    kernel=kernel, 
    name=SE_AGENT_NAME, 
    instructions=SE_AGENT_INSTRUCTIONS,
    )

    PO_agent = ChatCompletionAgent(
    id="agent", 
    kernel=kernel, 
    name=PO_AGENT_NAME, 
    instructions=PO_AGENT_INSTRUCTIONS,
    )

    # Chat agent group and termination strategy
    chat = AgentGroupChat(
        agents=[BA_agent, SE_agent, PO_agent],
        termination_strategy=ApprovalTerminationStrategy(agents=[PO_agent], maximum_iterations=10),
    )
    logger.info(f"User Input is : {input}")
    await chat.add_chat_message(ChatMessageContent(role=AuthorRole.USER, content=input))

    # Collect responses
    responses = []
    async for response in chat.invoke():
        responses.append({"role": response.role.value, "message": response.content})
    
    logger.info("Multi-agent conversation complete.")
    return responses
