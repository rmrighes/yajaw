# YAJAW - Yet Another Jira API Wrapper

[![PyPI - Version](https://img.shields.io/pypi/v/yajaw.svg)](https://pypi.org/project/yajaw)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/yajaw.svg)](https://pypi.org/project/yajaw)

-----

**Table of Contents**

- [Introduction](#introduction)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Introduction

There are several Python libraries to access Atlassian Jira, with just a few of them barely usable in the real world. Those few that pass the bar are usually designed using object oriented paradigm. I personaly prefer a functional paradigm when dealing with data-centric applications. Compound that with the need to extract, transform, and load the data in an effecient way and you'll understand why I chose to create my own library package.

The intention is to provide a package where we can access and manipulate the data in the Jira ecosystem primarily for project analysis and dashboarding. Focus in on read-only actions from the available REST APIs, using concurrent programming as much as possible.

API calls to modify the data in Jira are not excluded from the scope of the library package. They are just not prioritized to be addressed now.

## Installation

```console
pip install yajaw
```

## Usage

Under design...

## License

`yajaw` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
