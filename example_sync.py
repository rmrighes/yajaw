from yajaw import jira


def main():
    print("Resource: project")
    projects = jira.fetch_all_projects(expand=None)
    [print(project["key"]) for project in projects]
    print(f"There is a total of {len(projects)} projects.")

    print("Resource: projec/{project_key}")
    project = jira.fetch_project(project_key="ETOE", expand=None)
    print(project["key"])


if __name__ == "__main__":
    main()
