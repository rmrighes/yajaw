import asyncio
import logging
from dotenv import dotenv_values

config = dotenv_values()

JIRA_BASE_URL = config.get("JIRA_BASE_URL")
JIRA_API_V2 = config.get("JIRA_API_V2")
JIRA_AGILE_API_V1 = config.get("JIRA_AGILE_API_V1")
JIRA_GREENHOPPER_API = config.get("JIRA_GREENHOPPER_API")
JIRA_PAT = config.get("JIRA_PAT")

JIRA_API = JIRA_API_V2
JIRA_AGILE_API = JIRA_AGILE_API_V1

logger = logging.getLogger(__package__)
logging.getLogger("httpx").setLevel(logging.WARNING)
format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.INFO, format=format)

# TODO: Expose configuration settings for rate limit control
semaphore = asyncio.BoundedSemaphore(100)
