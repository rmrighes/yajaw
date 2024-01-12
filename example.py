import asyncio

from yajaw import jira


async def async_main():
    return None


def sync_main():
    use_fetch_all_projects()
    print()
    use_fetch_projects()
    print()
    use_fetch_projects_from_list()
    print()
    use_fetch_issue()
    print()
    use_search_issues()


def use_fetch_all_projects():
    print("RESOURCE: PROJECT")
    projects = jira.fetch_all_projects()
    if projects:
        for project in projects:
            print(f"Project key: {project['key']}")
        print(f"There is a total of {len(projects)} projects.\n")
    else:
        print("empty list!")


def use_fetch_projects():
    print("RESOURCE: PROJECT/{KEY}")
    project = jira.fetch_project(project_key="EMI")
    if project:
        print(f"Project key: {project['key']}")
    else:
        print("empty dictionary!")


def use_fetch_projects_from_list():
    print("RESOURCE: PROJECT FROM LIST")
    project_keys = ["ETOE", "ESTT", "EMI"]
    projects = jira.fetch_projects_from_list(project_keys=project_keys)
    if projects:
        for project in projects:
            print(f"Project key: {project['key']}")
        print(f"There is a total of {len(projects)} projects.\n")
    else:
        print("empty list!")


def use_fetch_issue():
    print("RESOURCE: ISSUE/{KEY}")
    issue = jira.fetch_issue(issue_key="ETOE-8")
    if issue:
        print(f"Issue key: {issue['key']}")
    else:
        print("empty dictionary!")


def use_search_issues():
    print("RESOURCE: SEARCH")
    jql = "project in (ETOE)"
    issues = jira.search_issues(jql=jql)
    if issues:
        for issue in issues:
            print(f"{issue['key']} - {issue['fields']['summary']}")
        print(f"There is a total of {len(issues)} projects.\n")
    else:
        print("empty list!")


if __name__ == "__main__":
    CONCURRENT = False

    if not CONCURRENT:
        sync_main()
    else:
        raise SystemExit(asyncio.run(async_main()))
