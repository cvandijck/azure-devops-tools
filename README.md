# azure-devops-tools

Set of practical tools to automate working with Azure Devops

More information can be found on the project's [website](https://github.com/cvandijck/azure-devops-tools).

## Installation

You can install adopt via pip:
```console
python -m pip install adopt
```

Alternatively, you can install adopt as a CLI tool using pipx:
```console
pipx install adopt
```

## Getting Started

Adopt is developed as a CLI tool to easily manage your Azure Devops project.
The tool is actively being developed and tools are continuously being added.

You can discover which tools are available by displaying the help page of the console script:

```console
adopt --help
```

### Backlog

These CLI tools help to manage your different backlogs in Azure Devops.

#### Print

Get a nicely formatted overview of your backlog in your terminal.

```console
adopt backlog print
```

#### Sort

Tired of cleaning up your backlog by dragging work items each time you had a backlog refinement or planning session?
With this short command you can automatically sort the backlog following the specific order you like.

```console
adopt backlog sort
```



