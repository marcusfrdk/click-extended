![Banner](../../assets/click-extended-documentation-banner.png)

# Tree

The `Tree` class is the central nervous system of `click-extended`. It manages the node hierarchy, coordinates lifecycle phases, and handles the registration and validation of all nodes in the context.

## Table of Contents

- [Lifecycle Phases](#lifecycle-phases)
- [Structure](#structure)

## Lifecycle Phases

The tree coordinates four distinct lifecycle phases for every command execution:

### Phase 1: Registration

Occurs when Python loads the module and decorators are applied. Nodes are queued in a pending state but not yet connected.

### Phase 2: Initialization

Occurs when the command is invoked. The Click context is created, and the `RootNode` initializes the tree structure. Metadata is injected into the context.

### Phase 3: Validation

The tree is built and validated.

- Parent/Child relationships are established.
- Tags are resolved.
- `ValidationNode.on_init()` hooks are executed.
- Structure integrity is checked (e.g., no orphans, valid hierarchy).

### Phase 4: Runtime

Parameters are processed and values are injected.

- Parent nodes load their values (from CLI, Env, etc.).
- Child nodes transform/validate values sequentially.
- `ValidationNode.on_finalize()` hooks are executed.
- The user's function is called with the processed values.

## Structure

The tree maintains several registries to track nodes:

| Registry   | Description                                                          |
| ---------- | -------------------------------------------------------------------- |
| `root`     | The single `RootNode` of the tree.                                   |
| `nodes`    | Dictionary of all registered nodes by name.                          |
| `parents`  | Dictionary of all `ParentNode` instances (Options, Arguments, Envs). |
| `children` | Dictionary of all `ChildNode` instances.                             |
| `tags`     | Dictionary of all `Tag` instances.                                   |
| `globals`  | List of global nodes (ValidationNodes).                              |
| `data`     | Custom data store for inter-node communication.                      |
