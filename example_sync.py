from yajaw import jira

def main():

    print("Resource: project")
    projects = jira.fetch_all_projects(expand=None)
    [print(project["key"]) for project in projects]
    print(f"There is a total of {len(projects)} projects.")
    print()
    print("Resource: projec/{project_key}")
    project = jira.fetch_project(project_key="ETOE", expand=None)
    print(project["key"])
    print()
    print("Resource: project/{project_key} from list")
    project_keys = {"ETOE","ESTT"}
    projects = jira.fetch_projects_from_list(project_keys=project_keys)
    [print(project["key"]) for project in projects]
    print()
    print("Resource: issue/{issue_key}")
    issue = jira.fetch_issue(issue_key="ETOE-8", expand=None)
    print(f"{issue["key"]} -- {issue["fields"]["summary"]}")
    print()
    print("Resource: search/{jql}")
    jql = "project in (ETOE, EMI, ESTT, MLOPS)"
    issues = jira.search_issues(jql=jql)
    [print(issue["key"]) for issue in issues]
    print(f"There is a total of {len(issues)} issues returned by the search.")
    print()

if __name__ == "__main__":
    main()
