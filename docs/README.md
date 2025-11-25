![Banner](../assets/click-extended-documentation-banner.png)

# Documentation

## Concepts

- [Root Node](./concepts/ROOT.md): A node that initializes a context and orchestrates the full lifecycle of the application.
- [Parent Node](./concepts/PARENT_NODE.md): A node that works like a data source and can have attached children.
- [Argument Node](./concepts/ARGUMENT_NODE.md): An extension of the parent node that injects a value from a positional argument in the command line.
- [Option Node](./concepts/OPTION_NODE.md): An extension of the parent node that injects a value from a keyword argument in the command line.
- [Child Node](./concepts/CHILD_NODE.md): A node that processes data through validation and transformation of the data from a data source.
- [Context](./concepts/CONTEXT.md): The context used across an application for data sharing, orchestration and synchronization of nodes.
- [Tree](./concepts/TREE.md): The structure used for storing the nodes of the current context.

## Nodes

- [Pre-built Validators](./nodes/DECORATORS.md): A full list of all pre-built validation decorators available to use in your application.
- [Pre-built Transformers](./nodes/DECORATORS.md): A full list of all pre-built transformer decorators available to use in your application.
- [Pre-built Globals](./nodes/DECORATORS.md): A full list of all pre-built global decorators available to use in your application.
- [`@argument`](./nodes/ARGUMENT.md): A parent node that reads data through positional arguments in the command line.
- [`@command`](./nodes/COMMAND.md): A root node that executes a function.
- [`@env`](./nodes/ENV.md): A parent node that reads an environment variable from your environment, supports both reading `.env` files and from the environment.
- [`@group`](./nodes/GROUP.md): A root node that allows nesting of other group- or command nodes to build a full command line interface.
- [`@option`](./nodes/OPTION.md): A parent node that reads data through keyword arguments in the command line.
- [`@tag`](./nodes/TAG.md): A special node that allows grouping of parent nodes through the `tags` parameter.

## Guides

- [Migrating From Click](./guides/MIGRATING_FROM_CLICK.md): A guide on how to migrate your codebase from `click` to `click-extended`.
