import asyncio
from yajaw import jira
from yajaw.core import rest


async def main():
    
    print("Resource: project")
    projects = await jira.async_fetch_all_projects(expand=None)
    [print(project["key"]) for project in projects]
    print(f"There is a total of {len(projects)} projects.")

    print("Resource: projec/{project_key}")
    project = await jira.async_fetch_project(project_key="ETOE", expand=None)
    print(project["key"])

    print("Resource: project/{project_key} from list")
    project_keys = {"ETOE","ESTT"}
    projects = await jira.async_fetch_projects_from_list(project_keys=project_keys)
    [print(project["key"]) for project in projects]

    print("Resource: issue/{issue_key} from list")
    issue_key = "ETOE-8"
    issue = await jira.async_fetch_issue(issue_key=issue_key)
    print(f"{issue["key"]} -- {issue["fields"]["summary"]}")

if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
