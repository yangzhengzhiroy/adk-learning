from google.adk import Agent

from story_teller.settings import DefaultModel, GenerateContentConfig
from story_teller import prompt


root_agent = Agent(
    model=DefaultModel,
    name="story_teller_agent",
    description="Create new stories for the user",
    instruction=prompt.STORY_TELLER_PROMPT,
    generate_content_config=GenerateContentConfig,
)
