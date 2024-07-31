from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager, register_function
import os
from tools import analyze_profile
import agentops

llm_config = {"model": "gpt-4o", "api_key": os.environ["OPENAI_API_KEY"]}

user_proxy = UserProxyAgent("user_proxy", code_execution_config=False)

linkedin_analyzer = AssistantAgent(
    name="linkedin_analyzer",
    system_message="""
      A LinkedIn analyzer who accurately describes profiles. 
      He calls the given tools to provide a description of a 
      LinkedIn profile.
    """,
    llm_config=llm_config
)

register_function(
    analyze_profile,
    caller=linkedin_analyzer,
    executor=user_proxy,
    name="analyze_profiles",
    description="Returns a detailed summary of the requested LinkedIn profile.",
)

writer = AssistantAgent(
    name="message_writer",
    system_message="""
      A LinkedIn message writer named Sebastian for ai-for-devs.com.
      Its role is to write short, highly individual LinkedIn messages 
      in the style of very experienced copywriter to introduce AI 
      consulting services based on the insights provided by the LinkedIn 
      Analyzer.
    """,
    llm_config=llm_config
)

groupchat = GroupChat(
    agents=[user_proxy, linkedin_analyzer, writer], messages=[]
)

manager = GroupChatManager(
    groupchat=groupchat, llm_config=llm_config
)

user_proxy.initiate_chat(
    manager,
    message=f"""
    Follow these steps:

    1. The analyzer asks the user for a given LinkedIn profile.
    2. Describe the profile in a few sentences.
    3. Write an individual LinkedIn message.
    4. Ask for the next LinkedIn profile.
    """
)