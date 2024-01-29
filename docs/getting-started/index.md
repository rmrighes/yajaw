## Installation

Ensure you have Python 3.11 or later before installing Yajaw. The package can be installed via `pip` using the following command:

```bash
pip install yajaw
```

Yajaw requires a dedicated configuration directory named `.yajaw`, located in your home directory. To ascertain the path to your home directory, run this Python script:

```python
from pathlib import Path

print(Path.home())
```

Should the `.yajaw` directory be absent, Yajaw will automatically create it and the necessary configuration files on first run. You are still responsible for providing your specific JIRA instance settings.

To configure, navigate to your home directory, open the `.yajaw` folder, and edit the `yajaw.toml` file. It contains default settings that you'll need to modify:

```toml
[jira]
token = "YOUR_PERSONAL_ACCESS_TOKEN"
base_url = "https://your-jira-domain.com"
server_api_v2 = "rest/api/2"
agile_api_v1 = "rest/agile/1.0"
greenhopper_api = "rest/greenhopper/1.0"

[retries]
tries = 10
delay = 0.0
backoff = 2.0

[requests]
timeout = 60

[concurrency]
semaphore_limit = 50

[pagination]
page_results = 40
```

Adjust the `token` and `base_url` with the correct values for your JIRA environment. If necessary, these adjustments can also be executed programmatically using the `yajaw.configuration` module. For further instructions, refer to the [User Guide](../user-guide/index.md).

## Basic Use

The fundamental use of Yajaw involves importing the `yajaw.jira` module and calling one of its functions. For example:

```python
from yajaw import jira

projects = jira.fetch_all_projects()

# Displays <class 'list'>
print(type(projects))
# Displays the type of each accessed project, which is <class 'dict'>
print(*[type(project) for project in projects], sep="\t")

# Ensure to replace "ABC" with a valid project key
project = jira.fetch_project(project_key="ABC")
# Displays <class 'dict'>
print(type(project))
```

An asynchronous code example for fetching projects can be written as follows:

```python
import asyncio
from yajaw import jira

async def main():
    projects = await jira.async_fetch_all_projects()

    # Displays <class 'list'>
    print(type(projects))
    # Displays the type of each accessed project, which is <class 'dict'>
    print(*[type(project) for project in projects], sep="\t")

    # Ensure to replace "ABC" with a valid project key
    project = await jira.async_fetch_project(project_key="ABC")
    # Displays <class 'dict'>
    print(f"Type: {type(project)}")

asyncio.run(main())
```

To understand Yajaw's function naming convention, consider the following pattern:

[`async_`] + `action` + `_` + `target_resource` + [`_from_list`]

Elements of the pattern:

- `async_`: An optional prefix for asynchronous functions. Omitted in synchronous functions.
- `action`: Represents the operation such as `fetch`, `create`, `update`, or `delete`.
- `target_resource`: Specifies the JIRA resource being accessed.
- `_from_list`: When used, it denotes a function operating on each element of a list.

Therefore, a function named `async_fetch_projects_from_list` would asynchronously execute `async_fetch_project` for every project given, with all calls happening in parallel, outputting a list of dictionaries, each representing a project.
