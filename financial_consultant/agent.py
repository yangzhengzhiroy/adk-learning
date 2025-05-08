import dotenv
dotenv.load_dotenv()

from google.adk.agents import Agent

from financial_consultant import prompt
from financial_consultant.settings import DefaultModel, GenerateContentConfig
from financial_consultant.sub_agents.finance.agent import financial_pipeline_agent
from financial_consultant.sub_agents.data_entry.agent import data_entry_agent


root_agent = Agent(
    model=DefaultModel,
    name="root_agent",
    description="A financial consutant agent helping with personal finance need.",
    instruction=prompt.ROOT_PROMPT,
    sub_agents=[financial_pipeline_agent, data_entry_agent],
    generate_content_config=GenerateContentConfig,
)
