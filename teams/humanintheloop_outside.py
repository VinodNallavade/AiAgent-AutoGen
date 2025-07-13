from autogen_ext.models.openai import AzureOpenAIChatCompletionClient
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
import asyncio
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.ui import Console
from autogen_agentchat.agents import AssistantAgent


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


assitant_1 = AssistantAgent("Writer", model_client=az_model_client,system_message="You are a creative writer who writes in less that 10 words.")
assitant_2 = AssistantAgent("Reviewer", model_client=az_model_client,system_message="You are a reviewer who reviews the work of the writer and provides feedback in less than 10 words. Please provide feedback in a constructive manner. And If the work is good, just say 'APPROVE' without any other comments.")
assitant_3 = AssistantAgent("Editor", model_client=az_model_client,system_message="You are an editor who edits the work of the writer based on the feedback from the reviewer and provides the final output in less than 10 words.")  

text_termination  = TextMentionTermination("APPROVE")

team = RoundRobinGroupChat(
    [assitant_1, assitant_2, assitant_3],max_turns=1)

async def main():
    task = "Write a 4-line poem about the ocean."

    while True:
        stream = team.run_stream(task=task)
        await Console(stream)

        feedback_from_human = input("Please provide feedback on the poem: ")
        if feedback_from_human.lower() == "approve":
            print("Task approved by human.")
            break
        else:
            task = f"Revise the poem based on the following feedback: {feedback_from_human}"
            print(f"Revising task: {task}")


if __name__ == "__main__":
    asyncio.run(main())