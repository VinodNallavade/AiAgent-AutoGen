from autogen_ext.models.openai import AzureOpenAIChatCompletionClient
from autogen_core.tools import FunctionTool
from autogen_agentchat.agents import AssistantAgent
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from langchain_tavily import TavilySearch
import os
from dotenv import load_dotenv


load_dotenv()
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
tavily_tool = TavilySearch( 
    api_key=TAVILY_API_KEY,
    max_results=5
)

def search(query: str) -> str:
    """Search the web for a given query and return the top result."""
    print(f"Searching for: {query}")
    if not query:
        return "No query provided."
    results = tavily_tool.run(query)
    #print(f"Search results: {results}")
    if not results:
        return "No results found."
    if results:
        return results
    else:
        return "No results found."


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


agent = AssistantAgent(
    "WebSearchAgent",description="An agent that can search the web for information using Tavily.",
    model_client=az_model_client,
    tools=[search],
    reflect_on_tool_use=True,
    system_message="You are a web search agent that can answer questions by searching the web." \
    " Use the search tool to find information and provide accurate answers.",
    )


async def main():
    result = await agent.run(task="Hi, can you search for the latest news on AI?")
    print(result.messages[-1].content)


if(__name__ == "__main__"):
    import asyncio
    asyncio.run(main())    
