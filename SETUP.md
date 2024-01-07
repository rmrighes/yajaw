# Setup

This page contains the basic instructions to setup and navigate within this project.

## Virtual Environment

Create and activate a new virtual environment using *venv*.

``` shell
python3 -m venv .venv
source .venv/bin/activate
```

Confirm the version of python that is being used. It should display a path to the version under the *.venv* folder.

``` shell
which python3
```

Update the pip installation within the newly created virtual environment.

``` shell
python3 -m pip install --upgrade pip
```

Install a Hatch as a program manager for Python.  

``` shell
python3 -m pip install --upgrade hatch
```
Attention: To completely clean the workspace, run the following command. It will remove everything not in the version control.

``` shell
git clean -dxffi
```

Run linter

``` shell
hatch run pylint $(git ls-files '*.py')
```
or
``` shell
hatch fmt
```