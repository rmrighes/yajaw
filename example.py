"""TBD"""
import asyncio

from yajaw import ApiType, jira
from yajaw.utils.decorators import duration


async def async_main():
    """TBD"""

    await use_async_fetch_all_projects()
    print()
    await use_async_fetch_projects()
    print()
    await use_async_fetch_projects_from_list()
    print()
    await use_async_fetch_issue()
    print()
    await use_async_fetch_issue_from_agile()
    print()
    await use_async_search_issues()
    print()
    # await use_async_fetch_sprints()
    # print()
    # await use_async_fetch_issues_from_sprints()


@duration
async def use_async_fetch_all_projects():
    """TBD"""
    print("ASYNC RESOURCE: PROJECT")
    projects = await jira.async_fetch_all_projects()
    if projects:
        for project in projects:
            print(f"Project key: {project['key']}")
        print(f"There is a total of {len(projects)} projects.")
    else:
        print("empty list!")


@duration
async def use_async_fetch_projects():
    """TBD"""
    print("ASYNC RESOURCE: PROJECT/{KEY}")
    project = await jira.async_fetch_project(project_key="EMI")
    if project:
        print(f"Project key: {project['key']}")
    else:
        print("empty dictionary!")


@duration
async def use_async_fetch_projects_from_list():
    """TBD"""
    print("ASYNC RESOURCE: PROJECT FROM LIST")
    project_keys = ["ETOE", "ESTT", "EMI"]
    projects = await jira.async_fetch_projects_from_list(project_keys=project_keys)
    if projects:
        for project in projects:
            print(f"Project key: {project['key']}")
        print(f"There is a total of {len(projects)} projects.")
    else:
        print("empty list!")


@duration
async def use_async_fetch_issue():
    """TBD"""
    print("ASYNC RESOURCE: ISSUE/{KEY}")
    issue = await jira.async_fetch_issue(issue_key="ETOE-8")
    if issue:
        print(f"Issue key: {issue['key']}")
    else:
        print("empty dictionary!")


@duration
async def use_async_fetch_issue_from_agile():
    """TBD"""
    print("ASYNC AGILE RESOURCE: ISSUE/{KEY}")
    issue = await jira.async_fetch_issue(
        issue_key="MLOPS-8724", agile=ApiType.AGILE, expand="changelog"
    )
    if issue:
        # story_points = "customfield_10012"
        print(f"Issue key: {issue['key']}")
        print(f"Estimate: {issue['fields']['customfield_10012']}")
        print(*(sprint for sprint in issue["fields"]["customfield_10631"]), sep="\n")
    else:
        print("empty dictionary!")


@duration
async def use_async_search_issues():
    """TBD"""
    print("ASYNC RESOURCE: SEARCH")
    jql = "project in (ETOE, ESTT, EMI, MLOPS)"
    issues = await jira.async_search_issues(jql=jql)
    if issues:
        for issue in issues:
            print(f"{issue['key']} - {issue['fields']['summary']}")
        print(f"There is a total of {len(issues)} projects.")
    else:
        print("empty list!")


@duration
async def use_async_fetch_sprints():
    """TBD"""
    print("ASYNC RESOURCE: sprint")
    # Continue implementation


@duration
async def use_async_fetch_issues_from_sprints():
    """TBD"""
    # Continue implementation


def sync_main():
    """TBD"""
    use_fetch_all_projects()
    print()
    use_fetch_projects()
    print()
    use_fetch_projects_from_list()
    print()
    use_fetch_issue()
    print()
    use_fetch_issue_from_agile()
    print()
    use_search_issues()
    print()
    # use_fetch_sprints()
    # print()
    # use_fetch_issues_from_sprints()


@duration
def use_fetch_all_projects():
    """TBD"""
    print("RESOURCE: PROJECT")
    projects = jira.fetch_all_projects()
    if projects:
        for project in projects:
            print(f"Project key: {project['key']}")
        print(f"There is a total of {len(projects)} projects.")
    else:
        print("empty list!")


@duration
def use_fetch_projects():
    """TBD"""
    print("RESOURCE: PROJECT/{KEY}")
    project = jira.fetch_project(project_key="EMI")
    if project:
        print(f"Project key: {project['key']}")
    else:
        print("empty dictionary!")


@duration
def use_fetch_projects_from_list():
    """TBD"""
    print("RESOURCE: PROJECT FROM LIST")
    project_keys = ["ETOE", "ESTT", "EMI"]
    projects = jira.fetch_projects_from_list(project_keys=project_keys)
    if projects:
        for project in projects:
            print(f"Project key: {project['key']}")
        print(f"There is a total of {len(projects)} projects.")
    else:
        print("empty list!")


@duration
def use_fetch_issue():
    """TBD"""
    print("RESOURCE: ISSUE/{KEY}")
    issue = jira.fetch_issue(issue_key="ETOE-8")
    if issue:
        print(f"Issue key: {issue['key']}")
    else:
        print("empty dictionary!")


@duration
def use_fetch_issue_from_agile():
    """TBD"""
    print("ASYNC AGILE RESOURCE: ISSUE/{KEY}")
    issue = jira.fetch_issue(issue_key="MLOPS-8730", expand="changelog", agile=ApiType.AGILE)
    if issue:
        # story_points = "customfield_10012"
        print(f"Issue key: {issue['key']}")
        print(f"Estimate: {issue['fields']['customfield_10012']}")
        print(*(sprint for sprint in issue["fields"]["customfield_10631"]), sep="\n")
    else:
        print("empty dictionary!")


@duration
def use_search_issues():
    """TBD"""
    print("RESOURCE: SEARCH")
    jql = "project in (ETOE, ESTT, EMI, MLOPS)"
    issues = jira.search_issues(jql=jql)
    if issues:
        for issue in issues:
            print(f"{issue['key']} - {issue['fields']['summary']}")
        print(f"There is a total of {len(issues)} projects.")
    else:
        print("empty list!")


@duration
def use_fetch_sprints():
    """TBD"""
    print("ASYNC RESOURCE: sprint")
    # Continue implementation


@duration
def use_fetch_issues_from_sprints():
    """TBD"""
    # Continue implementation


if __name__ == "__main__":
    CONCURRENT = False

    if not CONCURRENT:
        sync_main()
    else:
        raise SystemExit(asyncio.run(async_main()))
