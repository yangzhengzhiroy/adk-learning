from google.adk.agents import Agent, SequentialAgent

from financial_consultant import schema
from financial_consultant.settings import DefaultModel, GenerateContentConfig
from financial_consultant.sub_agents.finance import prompt


report_extract_agent = Agent(
    model=DefaultModel,
    name="report_extract_agent",
    description="Read user uploaded document and extract relevant information",
    instruction=prompt.REPORT_EXTRACT_PROMPT,
    output_schema=schema.Financials,
    generate_content_config=GenerateContentConfig,
)

math_agent = Agent(
    model=DefaultModel,
    name="math_agent",
    description="Perform mathematical calculation for information summarization",
    instruction=prompt.MATH_AGENT_PROMPT,
    input_schema=schema.Financials,
    output_schema=schema.FinancialSummary,
    generate_content_config=GenerateContentConfig,
)

financial_agent = Agent(
    model=DefaultModel,
    name="financial_agent",
    description="Analyze financial information and provide prescriptive insights to the user",
    instruction=prompt.FINANCIAL_PROMPT,
    input_schema=schema.FinancialSummary,
    generate_content_config=GenerateContentConfig,
)
financial_pipeline_agent = SequentialAgent(
    name="financial_pipeline_agent",
    description="the pipeline for financial analysis",
    sub_agents=[report_extract_agent, math_agent, financial_agent],
)
