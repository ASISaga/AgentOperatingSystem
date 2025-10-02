import os
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.prompt_template import PromptTemplateConfig

def build_kernel() -> Kernel:
    kernel = Kernel()
    # Configure your Azure OpenAI or other chat backend via environment variables
    service = AzureChatCompletion(
        deployment_name=os.environ["AZURE_OPENAI_DEPLOYMENT"],
        endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        api_key=os.environ["AZURE_OPENAI_API_KEY"]
    )
    kernel.add_service(service)
    return kernel

def legend_prompt(prompt: str, legend: str, principles: list[str]) -> PromptTemplateConfig:
    template = f"""
You are operating in legend mode: {legend}.
Apply these principles: {{{{principles}}}}.

Given the evidence:
{{{{evidence}}}}

Respond with:
- decision_scores: mapping of output labels to confidence (0-1)
- rationale: brief chain-of-thought summary (do not reveal full chain), citing principle IDs
- applied_principles: list of principle IDs
"""
    return PromptTemplateConfig(template=template, input_variables=["evidence", "principles"],
                                description=f"Legend scoring template for {legend}")
