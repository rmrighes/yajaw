"""
Module with examples for synchronous functions.
"""
from yajaw import YajawConfig, jira

projs = jira.fetch_all_projects()

for proj in projs:
    YajawConfig.LOGGER.info(f"Return from {__name__}: {proj['key']} -- {proj['name']}")

for _ in range(10):
    projs = jira.fetch_all_projects()


proj = jira.fetch_project(project_key="ETOE")
YajawConfig.LOGGER.info(f"Return from {__name__}: {proj['key']} -- {proj['name']}")


projs = jira.search_issues(jql="project in (ETOE)")
