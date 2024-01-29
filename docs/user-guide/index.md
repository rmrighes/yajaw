## Introduction

Yajaw is designed to streamline the integration with JIRA APIs, simplifying the programmable interactions by focusing on:

1. Enhancing accessibility to a breadth of JIRA resources (including those not officially supported)
2. Providing a user-friendly experience for both synchronous and asynchronous operations, ensuring rapid data retrieval

### Streamlined Access to Resources

Yajaw grants immediate access to an extensive range of JIRA resources, as outlined by:

* [Atlassian Developer Portal](https://developer.atlassian.com/cloud/jira/platform/rest/v2/intro)
* [Jira Data Center Platform REST API Reference](https://docs.atlassian.com/software/jira/docs/api/REST/latest)
* [Jira Agile Data Center REST API Reference](https://docs.atlassian.com/jira-software/REST/latest)

Our primary goal is to offer an intuitive means of querying resources, allowing users to retrieve data efficiently for analysis. The library represents data using built-in Python types, such as dictionaries or lists of dictionaries, ensuring a seamless transition to Python environments.

In instances where internal APIs provide exclusive access to JIRA's functionalities, Yajaw will attempt to expose parallel functions, facilitating data analysis endeavours even when confided to internal solutions.

#### Alternatives to the 'jira' Python Library

The popular [jira](https://pypi.org/project/jira/) Python library, around since 2011, is a comprehensive tool for JIRA REST API interactions. However, its complexity can be overbearing for straightforward data extraction tasks, as it encapsulates resources in custom objects. Yajaw simplifies this process by allowing direct function calls that correspond to specific methods and resources, delivering the output in accessible data structures. All essential access details such as base URL and personal access tokens are saved in a configuration file, eliminating redundant code for JIRA connection management.

### Fast Data Access with Synchronous and Asynchronous Support

Yajaw provides functions in both synchronous and asynchronous flavors, catering to varying coding preferences. Both function types utilize coroutines to efficiently handle multiple concurrent page requests, particularly when dealing with pagination. Even users who opt exclusively for synchronous operations can reap the benefits of simultaneous resource queries, striking an optimal balance between simplicity and performance.

## Basic topics

At this point of development, all necessary information is available in the [Getting Started](../getting-started/index.md). More content will be added here as the library evolves.

# Advanced topics

## Custom Logging Configuration for Yajaw

While Yajaw itself logs messages at different levels, it does not provide a built-in logging mechanism. It is the responsibility of the application to configure and enable logging. Setting up a custom logging configuration can significantly enhance monitoring, debugging, and recording operations within your applications. This section guides you through configuring a robust logging system that integrates seamlessly with Yajaw, offering structured, context-aware logging capabilities.

To see hands-on examples and for further guidance on integrating these logging practices with Yajaw, please refer to the [yajaw-examples](https://github.com/rmrighes/yajaw-examples) repository on GitHub.

### Tracking Execution Context

A `ContextVar` with a default `UUID` is defined to uniquely identify and track different parts of your application's operations or user sessions in the logs:

```python
from contextvars import ContextVar
import uuid

context_id: ContextVar[uuid.UUID] = ContextVar(
    "context_id", default=uuid.UUID("00000000-0000-0000-0000-000000000000")
)
```

### Implementing Custom Log Filters

The custom log filters, applied before the log records are emitted, serve specific purposes. Here are some as example:

```python
class ContextFilter(logging.Filter):
    def filter(self, record):
        record.context_id = str(context_id.get())
        return True
    
class QuotesFilter(logging.Filter):
    def filter(self, record):
        record.msg = record.msg.replace('\"', '\'')
        return True

class PIIFilter(logging.Filter):
    pii_pattern = re.compile(r"(email|password|ssn):\s*\S+", re.IGNORECASE)
    
    def filter(self, record):
        if self.pii_pattern.search(record.getMessage()):
            record.msg = self.pii_pattern.sub(r"\1: [REDACTED]", record.msg)
        return True
```

### Configuring Log Formatter to Output JSON

Logs are more readable and structurally consistent when formatted as JSON Lines. It is a convenient format for storing structured data that may be processed one record at a time. Each line in a JSON Lines file is a valid JSON object, separated by newline characters. Unlike a JSON file where the entire content represents a single JSON object or array, JSON Lines files simplify the storage of multiple, newline-delimited JSON objects.

```python
class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "asctime": self.formatTime(record, "%Y-%m-%dT%H:%M:%SZ"),
            "levelname": record.levelname,
            "context_id": getattr(record, "context_id", "no_context"),
            "name": record.name,
            "message": record.getMessage()
        }
        if record.exc_info:
            log_record["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(log_record)
```

### Managing Log File Rotation and Compression

The `rotator` and `namer` functions handle the log files' sizes and retention periods by compressing and renaming old log files.

```python
def rotator(source, dest):
    with open(source, "rb") as fs, gzip.open(dest, "wb") as fd:
        fd.writelines(fs)
    os.remove(source)
    
def namer(name):
    return name + ".gz"
```

### Setting Up Default Logging Configuration

This function creates a JSON configuration for the logging setup:

```python
def create_default_config(file_path):
    default_config = {
        "version": 1,
        "formatters": {"json": {"()": "observability.logs.JsonFormatter"}},
        "filters": {
            "context": {"()": "observability.logs.ContextFilter"},
            "piifilter": {"()": "observability.logs.PIIFilter"},
            "quotes":{"()": "observability.logs.QuotesFilter"}
        },
        "handlers": {
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "DEBUG",
                "formatter": "json",
                "filters": ["context", "piifilter", "quotes"],
                "filename": "logs/example.log",
                "maxBytes": 10485760,
                "backupCount": 10,
            }
        },
        "loggers": {
            "yajaw": {"handlers": ["file"], "level": "INFO", "propagate": True},
            "example": {"handlers": ["file"], "level": "INFO", "propagate": True},
            "httpx": {"handlers": ["file"], "level": "INFO", "propagate": True},
        },
    }
    with open(file_path, "w") as f:
        json.dump(default_config, f, indent=4, sort_keys=True)
```

Take into consideration the import path in the configuration above. In the provided example, it expects the filter classes to be at obserbility.logs. Adjust accordingly.
You should also adjust the logger name as needed.

### Initializing the Logging System

Finally, the `setup_logging` function ensures that the log directory exists, creates the config file if it does not exist, and applies the configuration to the logging system.

```python
def setup_logging():
    if not os.path.exists('logs'):
        os.makedirs('logs')
    config_file_path = 'logging_config.json'
    if not os.path.isfile(config_file_path):
        create_default_config(config_file_path)
    with open(config_file_path, 'r') as f:
        config = json.load(f)
    logging.config.dictConfig(config)
    for handler in logging.root.handlers:
        if isinstance(handler, logging.handlers.RotatingFileHandler):
            handler.rotator = rotator
            handler.namer = namer
```

### Example Usage 

After setting up logging using the `setup_logging` call at the application's start, you can log with context as follows:

```python
setup_logging()

logger = logging.getLogger("example")

# Within your application's operations
context_id.set(uuid.uuid4())  # Set a new context at the beginning of an operation
logger.info("This log message will have a unique context identifier.")
```

Logs produced by your application will include the unique `context_id` and be formatted as structured JSON, making them easier to search and analyze.
