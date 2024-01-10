"""Module responsible for serving as example of sync functions."""
import yajaw
from yajaw import jira


def main():
    """Main function used to execute the example."""

    my_logger = yajaw.CONFIG["log"]["logger"]

    my_logger.info("Resource: PROJECT")
    projects = jira.fetch_all_projects(expand={"expand": "description"})
    for project in projects:
        my_logger.info("Project key: %s", project["key"])
    my_logger.info("There is a total of %i projects.\n", len(projects))

    my_logger.info("Resource: PROJECT/{KEY}")
    project = jira.fetch_project(project_key="ETOE", expand={"expand": "description"})
    my_logger.info("Project key: %s\n", project["key"])

    my_logger.info("Resource: PROJECT/{KEY} from list")
    project_keys = {"ETOE", "ESTT"}
    projects = jira.fetch_projects_from_list(
        project_keys=project_keys, expand={"expand": "description"}
    )
    for project in projects:
        my_logger.info("Project key: %s", project["key"])
    my_logger.info("There is a total of %i projects.\n", len(projects))

    my_logger.info("Resource: ISSUE/{KEY} from list")
    issue = jira.fetch_issue(issue_key="ETOE-8", expand={"expand": "changelog"})
    my_logger.info("%s - %s", issue["key"], issue["fields"]["summary"])
    my_logger.info(
        "A total of %i change(s) in the changelog.\n", issue["changelog"]["total"]
    )

    my_logger.info("Resource: SEARCH/{JQL}")
    jql = "project in (ETOE, EMI, ESTT, MLOPS)"
    issues = jira.search_issues(
        jql=jql, expand={"expand": "description"}, field="issues"
    )
    my_logger.info(
        "There is a total of %i issues returned by the search.\n", len(issues)
    )


if __name__ == "__main__":
    main()
