# Azure OpenAI Configuration (for fine-tuning)
azure_openai_model = "gpt-4-turbo-2024-04-09"  # GPT-4.1 equivalent
azure_openai_endpoint = ""  # Set your Azure OpenAI endpoint
azure_openai_key = ""  # Set your Azure OpenAI key
azure_openai_api_version = "2024-02-01"

# Amazon Bedrock Configuration (for Claude Sonnet 4)
aws_region = "us-east-1"  # Or your preferred region
aws_access_key_id = ""  # Set your AWS access key
aws_secret_access_key = ""  # Set your AWS secret key
bedrock_model_id = "anthropic.claude-3-5-sonnet-20241022-v2:0"  # Claude Sonnet 4

# Legacy model for backward compatibility
model = azure_openai_model