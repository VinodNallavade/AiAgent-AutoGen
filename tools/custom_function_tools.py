from autogen_ext.models.openai import AzureOpenAIChatCompletionClient
from autogen_core.tools import FunctionTool
from autogen_agentchat.agents import AssistantAgent
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
import asyncio
from pydantic import BaseModel,Field



class output_format(BaseModel):
    input : str =Field(description="Input from the user")
    description : str = Field(description="Output description")

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


def add_numbers(num1 : int, num2:int)-> int:
    """ This tool will be used to add two numbers
         input is num1 and num2 of integer type
         output  is integer type
    """
    return num1+num2


tool= FunctionTool(add_numbers,description="A tool for adding number")

agent = AssistantAgent("ArthematicOperator",az_model_client,tools=[tool],reflect_on_tool_use= True,tool_call_summary_format=output_format)


async def main():
    result = await agent.run(task="Add 2 with 3")
    print(result.messages[-1].content)


if(__name__ == "__main__"):
    asyncio.run(main())
