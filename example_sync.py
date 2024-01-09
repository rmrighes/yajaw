"""Module responsible for serving as example of sync functions."""
from yajaw import jira


def main():
    """Main function used to execute the example."""

    print("Resource: project")
    projects = jira.fetch_all_projects(
        expand={"expand":"description"})
    print(* (project["key"] for project in projects), sep="\n")
    print(f"There is a total of {len(projects)} projects.")
    print()
    print("Resource: projec/{project_key}")
    project = jira.fetch_project(
        project_key="ETOE",
        expand={"expand":"description"})
    print(project["key"])
    print()
    print("Resource: project/{project_key} from list")
    project_keys = {"ETOE","ESTT"}
    projects = jira.fetch_projects_from_list(
        project_keys=project_keys,
        expand={"expand":"description"})
    print(* (project["key"] for project in projects), sep="\n")
    print()
    print("Resource: issue/{issue_key}")
    issue = jira.fetch_issue(
        issue_key="ETOE-8",
        expand={"expand":"changelog"})
    print(f"{issue["key"]} -- {issue["fields"]["summary"]}")
    print(f"A total of {issue["changelog"]["total"]} change(s) in the changelog.")
    print()
    print("Resource: search/{jql}")
    jql = "project in (ETOE, EMI, ESTT, MLOPS)"
    issues = jira.search_issues(
        jql=jql,
        expand={"expand":"description"},
        field="issues")
    print(* (f"{issue["key"]} - {issue["fields"]["summary"]}" for issue in issues), sep="\n")
    print(f"There is a total of {len(issues)} issues returned by the search.")
    print()

if __name__ == "__main__":
    main()
