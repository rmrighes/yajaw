from yajaw import jira

def main():

    print("Resource: project")
    projects = jira.fetch_all_projects(expand=None)
    [print(project["key"]) for project in projects]
    print(f"There is a total of {len(projects)} projects.")

    print("Resource: projec/{project_key}")
    project = jira.fetch_project(project_key="ETOE", expand=None)
    print(project["key"])

    print("Resource: project/{project_key} from list")
    project_keys = {"ETOE","ESTT"}
    projects = jira.fetch_projects_from_list(project_keys=project_keys)
    [print(project["key"]) for project in projects]

    print("Resource: issue/{issue_key}")
    issue = jira.fetch_issue(issue_key="ETOE-8", expand=None)
    print(f"{issue["key"]} -- {issue["fields"]["summary"]}")

    # TODO: Return all pages. It is returning only the maxResults amount.
    print("Resource: search/{jql}")
    jql = "project = ETOE"
    issues = jira.search_issues(jql=jql)
    [print(issue["key"]) for issue in issues]

if __name__ == "__main__":
    main()
