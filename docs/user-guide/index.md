## Introduction

Yajaw was designed to address two main aspects when dealing with JIRA APIs programatically:

1. Ease of access to supported (and unsupported) resources
1. Ease of use in both synchronous and asynchronous code, promoting speedy retrieval of data

### Access to supported (and unsupported) resources

JIRA resources supported by this library are documented in places like:

* [Atlassian Developer portal](https://developer.atlassian.com/cloud/jira/platform/rest/v2/intro)
* [Jira Data Center platform REST API reference](https://docs.atlassian.com/software/jira/docs/api/REST/latest)
* [Jira Agile Data Center REST API reference](https://docs.atlassian.com/jira-software/REST/latest)

Emphasis is given to read existing resources in the most straightforward way as possible, with the intent of making the data available for data analysis.
It means that the data is represented in Python's buit-in types. Typically, it means representing the resource as a dictionary or list of dictionaries.

Some resources might be available in internal APIs used by JIRA. When it makes sense, we'll expose similar functions to access them if it is the only path to solve challenges for data analysis.

**Why not use the jira library?**

A third-party Python library for interacting with JIRA via REST APIs named [jira](https://pypi.org/project/jira/) is available since 2011. It is the de facto library for interacting with JIRA resources and properties. What makes it powerful also makes it complex for the intended purpose. As resources and properties are represented as custom objects, it makes unnecessarily complex to use them for simple data extraction.

Overall, the intent is to simply invoke a function that represents a method and resource, and save the result as a dictionary or list of dictionaries. Al access information, like base url or personal access token, are stored in a confiration file. There's no need for adding code for JIRA connection management if you choose to do so.

### Speedy access to data, with both sync and async support

Functions have both sync and async counterparts. You just pick and use the ones that are more appropriate for your code. Both of them will leverage coroutines to request multiple pages at once when pagination is supported. You can completely ignore async code and still benefit from concurrent requests to resources.