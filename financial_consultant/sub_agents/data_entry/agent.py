from google.adk.agents import Agent
from google.adk.tools import FunctionTool

from financial_consultant.settings import DefaultModel, GenerateContentConfig
from financial_consultant.tools import financial_update
from financial_consultant.sub_agents.data_entry import prompt


data_entry_agent = Agent(
    model=DefaultModel,
    name="data_entry_agent",
    instruction=prompt.DATA_ENTRY_PROMPT,
    tools=[FunctionTool(financial_update)],
    generate_content_config=GenerateContentConfig,
)
