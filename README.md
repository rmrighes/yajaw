# YAJAW - Yet Another Jira API Wrapper

YAJAW is an intuitive Python library designed to simplify interactions with Atlassian's JIRA APIs. Aimed at developers, data analysts, and project managers, Yajaw facilitates seamless integration of JIRA's extensive API offerings into your Python projects with ease of use, concurrency support, and efficient handling of paginated resources.

[![PyPI - Version](https://img.shields.io/pypi/v/yajaw.svg)](https://pypi.org/project/yajaw)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/yajaw.svg)](https://pypi.org/project/yajaw)
[![Documentation Status](https://readthedocs.org/projects/yajaw/badge/?version=latest)](https://yajaw.readthedocs.io/en/latest/?badge=latest)

## Features

- **Functional Paradigm**: Designed with a preference for functional programming to handle data-centric operations efficiently.
- **Concurrent Pagination**: Handles paginated resources concurrently, speeding up data retrieval.
- **Ease of Access**: Interact with both supported and unsupported JIRA REST APIs.
- **Simple Configuration**: Easy setup with a TOML configuration file.
- **Dual Support**: Supports both synchronous and asynchronous programming styles.

## Quickstart

1. **Installation**

   Ensure you have Python 3.11 or later before installing Yajaw. The package can be installed via `pip` using the following command:

   ```bash
   pip install yajaw
   ```

2. **Configuration**

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

   Adjust the `token` and `base_url` with the correct values for your JIRA environment. If necessary, these adjustments can also be executed programmatically using the `yajaw.configuration` module. For further instructions, refer to the [User Guide](https://yajaw.readthedocs.io/en/latest/user-guide/index.html).

3. **Basic Usage**

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

## Documentation

For more in-depth examples and usage instructions, visit the [official YAJAW documentation](https://yajaw.readthedocs.io/).

## Issues

If you encounter any issues or have suggestions for the project, please use the [GitHub Issues](https://github.com/unknown/rmrighes/issues) page.

## Contributing

Contributions are welcome! For more information on how to contribute, please refer to our contribution guidelines outlined in the documentation.

## License

YAJAW is distributed under the MIT License. See `LICENSE` for more details.

## Links

- Documentation: [https://yajaw.readthedocs.io/](https://yajaw.readthedocs.io/)
- Source Code: [https://github.com/rmrighes/yajaw](https://github.com/rmrighes/yajaw)
- Issues: [https://github.com/unknown/rmrighes/issues](https://github.com/unknown/rmrighes/issues)
