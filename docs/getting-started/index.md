## Installation


Package requires Python version >= 3.11 and can be installed via pip.

``` linenums="0"
pip install yajaw
```

Library expects for a specifc folder where the configuration files for the library and logging are available. Folder name is `.yajaw` and is expected to exist in your home folder.
You can confirm where exactly this folder is by running the code:

``` py linenums="1"
from pathlib import Path

print(Path.home())
```

Library will create the folder and required files if is doesn't detect them. You still have to provide the specific settings for your JIRA instance.

Go to your home file and open the `yajaw.toml` file under `.yajaw` folder. It should look like:

``` toml
[jira]
token = "CHANGE--Insert-PAT"
base_url = "CHANGE--https://my-jira-domain.com"
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

Make the necessary adjustments on `token` and `base_url` key/value pairs under the `jira` header and save the file. Same can be accomplished programmatically via `yajaw.configuration` module. Refer to the [User Guide](../user-guide/index.md) for more details.


## Basic use

Most basic use of the library is done by importing the `yajaw.jira` module and calling one of its functions. For example: 

``` py linenums='1'
from yajaw import jira

projects = jira.fetch_all_projects()

# <class 'list'>
print(type(projects))
# As many <class 'dict'> as projects you have access to
print(*[type(project) for project in projects], sep="\t")

# Replace with a valid project key
project = jira.fetch_project(project_key="ABC")
# <class 'dict'>
print(type(project))

```

Not that is a really useful example, but here is how to write an asynchronous version for the code above:

``` py linenums='1'
import asyncio
from yajaw import jira

async def main():

    projects = await jira.async_fetch_all_projects()

    # <class 'list'>
    print(type(projects))
    # As many <class 'dict'> as projects you have access to
    print(*[type(project) for project in projects], sep="\t")

    # Replace with a valid project key
    project =  await jira.async_fetch_project(project_key="ABC")
    # <class 'dict'>
    print(f"Type: {type(project)}")

asyncio.run(main())

```

As a rule of thumb, the functions follow a simple naming convention:

[`async_`] + `verb` + _ + `resource` + [`_from_list`], where:

* [`async_`]: It is a prefix used in asynchrnous functions. Synch functions don't have the prefix.
* `verb`: one of following verbs:
    - `fetch` is used to read existing resources.
    - `create` is used to create a new resource.
    - `update` is used to update an existing resource.
    - `delete` is used to remove an existing resource.
* `resource`: It is the name of the accessed resource. It can include the `all` adverb.
* [`from_list`]: It is used to call a basic function, one for each element of the list.

So a function named `async_fetch_projects_from_list` will call `async_fetch_project` for each project listed. Multiple calls will be made in parallel since the code is asynchronous. Each project will be represented in a dictionary that belongs to a list.