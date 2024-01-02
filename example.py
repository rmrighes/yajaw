import asyncio
from time import perf_counter
from yajaw import api as jira_api


async def main() -> None:
    time_start = perf_counter()
    projects = await jira_api.get_all_projects()
    time_finish = perf_counter()
    print(f"Total get_all_projects time is {time_finish - time_start} seconds.")
    search_keys = list()
    for project in projects:
        search_keys.append(project["key"])

    time_start = perf_counter()
    project = await jira_api.get_project("EMI")
    time_finish = perf_counter()
    print(f"Total get_project time is {time_finish - time_start} seconds.")

    time_start = perf_counter()
    projects = await jira_api.get_projects_from_list(search_keys)
    time_finish = perf_counter()
    print(f"Total get_projects_from_list time is {time_finish - time_start} seconds.")
    print(f"There is a total of {len(projects)} projects in the response.")

    jql = f'project = ETOE'
    time_start = perf_counter()
    response = await jira_api.search_issues_jql(jql)
    time_finish = perf_counter()
    print(f"Total get_projects_from_list time is {time_finish - time_start} seconds.")

    proj_key = "ETOE"
    response = await jira_api.get_issues_from_project(key=proj_key)
    print(len(response))

    time_start = perf_counter()
    proj_key = ["ETOE", "ESTT"]
    response = await jira_api.get_issues_from_project(key=proj_key)
    for issue in response:
        print(f'{issue["fields"]["project"]["name"]} :: {issue["key"]}')
    print(len(response))
    time_finish = perf_counter()
    print(f"Total get_issues_from_projects is {
          time_finish - time_start} seconds.")


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
