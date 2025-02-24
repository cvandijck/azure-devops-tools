# azure-devops-tools

Set of practical tools to automate working with Azure Devops

More information can be found on the project's [website](https://github.com/cvandijck/azure-devops-tools).

## Installation

The preferred way to install `adopt` to use as a global CLI tool is to install it via `uv` and run it via `uvx`, the `pipx` variant for the `uv` package manager.

If you don't have `uv` and `uvx` installed yet, you can install it by running:

```console
winget install --id=astral-sh.uv
```

or by following the instructions on the [uv website](https://docs.astral.sh/uv/).

After installing `uv`, you can install `adopt` as a uv tool by running:

```console
uv tool install adopt
```

and then run the tool by running:

```console
uvx adopt
```

Alternatively, you can install `adopt` as a CLI tool using pip or globally using pipx:

```console
python -m pip install adopt
```

Or install it as a global CLI tool using pipx:

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
adopt backlog print --url <azure_devops_org_url> --token <azure_devops_personal_token> --project <azure_devops_project> --team <azure_devops_team> --category <azure_devops_work_item_category>
```

#### Sort

Tired of cleaning up your backlog by dragging work items each time you had a backlog refinement or planning session?
With this short command you can automatically sort the backlog following the specific order you like.

```console
adopt backlog print --url <azure_devops_org_url> --token <azure_devops_personal_token> --project <azure_devops_project> --team <azure_devops_team> --category <azure_devops_work_item_category> --sort_key <azure_devops_work_item_field>
```

The `--sort_key` argument determines the order in which the work items will be sorted in the backlog. The value of the `--sort_key` argument should be a string of characters, where each character represents a field of the work item. The order of the characters in the string determines the order in which the work items will be sorted. In lower case, an acending order is used. When capitalized, the item will be sorted in descending order. The following characters are supported:

i
: Iteration path

p
: Priority

t
: Title

r
: Rank

For example, the default sorting key `Iprt` command will sort the work items in the backlog first by *iteration path* in descending order (bringing the latest iteration on top), then followed by *priority*, *parent rank* and *title* in ascending order, bringing highest prio work items to the top, with additional sorting by parent item ranking and finally title.

#### Debug logging
Each command has logging functionality built in. The level of logging can be set by using the `--log-level` argument. The default log level is `INFO`.

### Configuration
Coming soon

## Contribute

In `adopt`, the incredibly fast package manager `uv` is used to setup and manage the project. To get started with the project, you can install `uv` by running:

```console
winget install --id=astral-sh.uv
```

or by following the instructions on the [uv website](https://docs.astral.sh/uv/).

After installing `uv`, you can setup the project by running:

```console
uv sync
```
For convenience, most operations required to contribute or manage this project are available as `make` commands.
