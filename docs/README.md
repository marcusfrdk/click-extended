![Banner](../assets/click-extended-documentation-banner.png)

# Documentation

## Core

- [Root Node](./core/ROOT_NODE.md): A node that initializes a context and orchestrates the full lifecycle of the application.
- [Parent Node](./core/PARENT_NODE.md): A node that works like a data source and can have attached children.
- [Argument Node](./core/ARGUMENT_NODE.md): An extension of the parent node that injects a value from a positional argument in the command line.
- [Option Node](./core/OPTION_NODE.md): An extension of the parent node that injects a value from a keyword argument in the command line.
- [Child Node](./core/CHILD_NODE.md): A node that processes data through validation and transformation of the data from a data source.
- [Context](./core/CONTEXT.md): The context used across an application for data sharing, orchestration and synchronization of nodes.
- [Tree](./core/TREE.md): The structure used for storing the nodes of the current context.

## Guides

- [Migrating From Click](./guides/MIGRATING_FROM_CLICK.md): A guide on how to migrate your codebase from `click` to `click-extended`.
