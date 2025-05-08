import os
import sys
import vertexai
from vertexai import agent_engines
from vertexai.preview.reasoning_engines import AdkApp
from dotenv import load_dotenv
load_dotenv()

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from financial_consultant.agent import root_agent



vertexai.init(
    project=os.environ["GOOGLE_CLOUD_PROJECT"],
    location=os.environ["GOOGLE_CLOUD_LOCATION"],
    staging_bucket=f"gs://{os.environ['GOOGLE_CLOUD_STORAGE_BUCKET']}",
)

app = AdkApp(
    agent=root_agent,
)

print("Remote app creation starts...")
remote_app = agent_engines.create(
    app,
    requirements=[
        "cloudpickle==3.1.1",
        "google-adk>=0.3.0",
        "google-cloud-aiplatform[agent_engines]",
        "google-cloud-secret-manager>=2.23.3",
        "google-cloud-storage>=2.19.0",
        "gspread>=6.2.0",
    ],
    extra_packages=[
        "./financial_consultant",
    ]
)
print("Remote app creation complete.")
