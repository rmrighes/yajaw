"""Module responsible for serving as example of functions."""
import asyncio

import yajaw
from yajaw import jira
from yajaw.core import exceptions


async def async_main():
    """Main sync function used to execute the example."""

    my_logger = yajaw.CONFIG["log"]["logger"]

    my_logger.info("ASYNC -- Resource: PROJECT")
    projects = await jira.async_fetch_all_projects(expand={"expand": "description"})
    for project in projects:
        my_logger.info("Project key: %s", project["key"])
    my_logger.info("There is a total of %i projects.\n", len(projects))

    my_logger.info("ASYNC -- Resource: PROJECT/{KEY}")
    project = await jira.async_fetch_project(project_key="ETOE", expand={"expand": "description"})
    my_logger.info("Project key: %s\n", project["key"])

    my_logger.info("ASYNC -- Resource: PROJECT/{KEY} from list")
    project_keys = {"ETOE", "ESTT"}
    projects = await jira.async_fetch_projects_from_list(
        project_keys=project_keys, expand={"expand": "description"}
    )
    for project in projects:
        my_logger.info("Project key: %s", project["key"])
    my_logger.info("There is a total of %i projects.\n", len(projects))

    my_logger.info("ASYNC -- Resource: ISSUE/{KEY} from list")
    issue_key = "ETOE-8"
    issue = await jira.async_fetch_issue(issue_key=issue_key, expand={"expand": "changelog"})
    my_logger.info("%s - %s", issue["key"], issue["fields"]["summary"])
    my_logger.info("A total of %i change(s) in the changelog.\n", issue["changelog"]["total"])

    my_logger.info("ASYNC -- Resource: SEARCH/{JQL}")
    jql = "project in (ETOE, EMI, ESTT, MLOPS)"
    issues = await jira.async_search_issues(jql=jql, expand={"expand": "changelog"}, field="issues")
    my_logger.info("There is a total of %i issues returned by the search.\n", len(issues))


def sync_main():
    """Main async function used to execute the example."""

    my_logger = yajaw.CONFIG["log"]["logger"]

    my_logger.info("SYNC -- Resource: PROJECT")
    projects = jira.fetch_all_projects(expand={"expand": "description"})
    for project in projects:
        my_logger.info("Project key: %s", project["key"])
    my_logger.info("There is a total of %i projects.\n", len(projects))

    my_logger.info("SYNC -- Resource: PROJECT/{KEY}")
    project = jira.fetch_project(project_key="ETOE", expand={"expand": "description"})
    my_logger.info("Project key: %s\n", project["key"])

    my_logger.info("SYNC -- Resource: PROJECT/{KEY} from list")
    project_keys = {"ETOE", "ESTT"}
    projects = jira.fetch_projects_from_list(
        project_keys=project_keys, expand={"expand": "description"}
    )
    for project in projects:
        my_logger.info("Project key: %s", project["key"])
    my_logger.info("There is a total of %i projects.\n", len(projects))

    my_logger.info("SYNC -- Resource: ISSUE/{KEY} from list")
    issue_key = "ETOE-8"
    issue = jira.fetch_issue(issue_key=issue_key, expand={"expand": "changelog"})
    my_logger.info("%s - %s", issue["key"], issue["fields"]["summary"])
    my_logger.info("A total of %i change(s) in the changelog.\n", issue["changelog"]["total"])

    my_logger.info("SYNC -- Resource: SEARCH/{JQL}")
    try:
        jql = "project in (ETOE, EMI, ESTT, MLOPS)"
        issues = jira.search_issues(jql=jql, expand={"expand": "description"}, field="issues")
        my_logger.info("There is a total of %i issues returned by the search.\n", len(issues))
    except exceptions.InvalidResponseError:
        my_logger.info("Exiting without result - a valid response was never received.")


if __name__ == "__main__":
    CONCURRENT = False

    if not CONCURRENT:
        sync_main()
    else:
        raise SystemExit(asyncio.run(async_main()))
