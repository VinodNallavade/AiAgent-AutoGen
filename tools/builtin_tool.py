from autogen_ext.models.openai import AzureOpenAIChatCompletionClient
from autogen_core.tools import FunctionTool
from autogen_agentchat.agents import AssistantAgent
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
import asyncio
from pydantic import BaseModel,Field
from autogen_ext.tools.http import HttpTool



# Create the token provider
token_provider = get_bearer_token_provider(
    DefaultAzureCredential(),
    "https://cognitiveservices.azure.com/.default",
)

az_model_client = AzureOpenAIChatCompletionClient(
    azure_deployment="gpt-4o-mini",
    model="gpt-4o-mini",
    api_version="2024-08-01-preview",
    azure_endpoint="https://azopenai-langchain.openai.azure.com/",
    azure_ad_token_provider=token_provider,  # Optional if you choose key-based authentication.
    # api_key="sk-...", # For key-based authentication.
)


output_format = {
                "title": "CatFact model",
                "description": "CatFact",
                "properties": {
                    "fact": {
                        "title": "Fact",
                        "description": "Fact",
                        "type": "string",
                        "format": "string"
                    },
                    "length": {
                        "title": "Length",
                        "description": "Length",
                        "type": "integer",
                        "format": "int32"
                    }
                },
                "type": "object"
            }

http_tool = HttpTool(
    name="HttpTool",
    description="A tool for making HTTP requests",
    method="GET",
    headers={"Accept": "application/json"},  
    scheme= "https",
    port=443,
    path="/fact",
    host="catfact.ninja",  # The host for the HTTP request
     json_schema=output_format,
)



agent = AssistantAgent(
    "HttpAgent",description="An agent that uses HTTP tool",
    model_client=az_model_client,tools=[http_tool],
    reflect_on_tool_use=True)




async def main():
    result = await agent.run(task="Get a random cat fact")
    print(result.messages[-1].content)


if(__name__ == "__main__"):
    asyncio.run(main())
