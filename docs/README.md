![Banner](../assets/click-extended-documentation-banner.png)

# Documentation

## Concepts

- [Root Node](./concepts/ROOT.md): A node that initializes a context and orchestrates the full lifecycle of the application.
- [Parent Node](./concepts/PARENTS.md): A node that works like a data source and can have attached children.
- [Global Node](./concepts/PARENTS.md): A node that works like a data source but can not have attached children.
- [Child Node](./concepts/PARENTS.md): A node that processes data through validation and transformation of the data from a data source.
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

## Usage

- [Examples](./usage/EXAMPLES.md): Examples of how to use the library and some ideas of real-world applications.
- [Errors](./usage/ERRORS.md): How and when to use various errors and how the error system works.
- [Aliasing](./usage/ALIASING.md): How aliasing works and how to use it.
- [Sync and Async](./usage/SYNC_AND_ASYNC.md.md): How to use both synchronous and asynchronous functions and methods.

## Guides

- [Migrating From Click](./guides/MIGRATING_FROM_CLICK.md): A guide on how to migrate your codebase from `click` to `click-extended`.
- [Create a Child](./guides/CREATE_CHILD.md): A guide on how to create a new custom child for validating and processing data.
- [Create a Parent](./guides/CREATE_PARENT.md): A guide on how to create a new parent that allows custom data fetching with the ability to post-process the data.
- [Create a Global](./guides/CREATE_GLOBAL.md): A guide on how to create a new global that allows custom data fetching without the ability to post-proces the data.
