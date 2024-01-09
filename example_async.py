"""Module responsible for serving as example of async functions."""
import asyncio

from yajaw import jira


async def main():
    """Main function used to execute the example."""

    print("Resource: project")
    projects = await jira.async_fetch_all_projects(expand={"expand":"description"})
    print(* (project["key"] for project in projects), sep="\n")
    print(f"There is a total of {len(projects)} projects.")
    print()
    print("Resource: projec/{project_key}")
    project = await jira.async_fetch_project(
        project_key="ETOE", expand={"expand":"description"})
    print(project["key"])
    print()
    print("Resource: project/{project_key} from list")
    project_keys = {"ETOE","ESTT"}
    projects = await jira.async_fetch_projects_from_list(
        project_keys=project_keys,expand={"expand":"description"})
    print(* (project["key"] for project in projects), sep="\n")
    print()
    print("Resource: issue/{issue_key} from list")
    issue_key = "ETOE-8"
    issue = await jira.async_fetch_issue(
        issue_key=issue_key,expand={"expand":"changelog"})
    print(f"{issue["key"]} -- {issue["fields"]["summary"]}")
    print()
    print("Resource: search/{jql}")
    jql = "project in (ETOE, EMI, ESTT, MLOPS)"
    issues = await jira.async_search_issues(
        jql=jql, expand={"expand":"changelog"}, field="issues")
    print(* (f"{issue["key"]} - {issue["fields"]["summary"]}" for issue in issues), sep="\n")
    print(f"There is a total of {len(issues)} issues returned by the search.")
    print()

if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
