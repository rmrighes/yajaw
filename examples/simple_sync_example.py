"""
Module with examples for synchronous functions.
"""
from yajaw import jira

projs = jira.fetch_all_projects()

for proj in projs:
    print(f"{proj['key']:<20} {proj['name']:<40}")

print()

for _ in range(10):
    projs = jira.fetch_all_projects()

print()

proj = jira.fetch_project(project_key="ETOE")

print()

projs = jira.search_issues(jql="project in (ETOE)")
