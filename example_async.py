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


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
