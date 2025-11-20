![Banner](../assets/click-extended-documentation-banner.png)

# Transformers

Transformers are pre-built [child nodes](./CHILD_NODE.md) and are imported from the `click_extended.transform` module.

## Strings

| Name                    | Description                                 | Type (Singular) | Type (Tuple) | Tuple(Nested Tuple) |
| ----------------------- | ------------------------------------------- | --------------- | ------------ | ------------------- |
| to_camel_case           | Convert a string to `camelCase`.            | `str`           | `str`        | `str`               |
| to_dot_case             | Convert a string to `dot.case`.             | `str`           | `str`        | `str`               |
| to_flat_case            | Convert a string to `flatcase`.             | `str`           | `str`        | `str`               |
| to_kebab_case           | Convert a string to `kebab-case`.           | `str`           | `str`        | `str`               |
| to_lower_case           | Convert a string to `lower case`.           | `str`           | `str`        | `str`               |
| to_meme_case            | Convert a string to `meMe CaSe`.            | `str`           | `str`        | `str`               |
| to_pascal_case          | Convert a string to `PascalCase`.           | `str`           | `str`        | `str`               |
| to_path_case            | Convert a string to `path/case`.            | `str`           | `str`        | `str`               |
| to_screaming_snake_case | Convert a string to `SCREAMING_SNAKE_CASE`. | `str`           | `str`        | `str`               |
| to_snake_case           | Convert a string to `snake_case`.           | `str`           | `str`        | `str`               |
| to_title_case           | Convert a string to `Title Case`.           | `str`           | `str`        | `str`               |
| to_train_case           | Convert a string to `Train-Case`.           | `str`           | `str`        | `str`               |
| to_upper_case           | Convert a string to `UPPER CASE`.           | `str`           | `str`        | `str`               |

## Files

| Name    | Description                                                               | Type (Singular) | Type (Tuple)  | Tuple(Nested Tuple) |
| ------- | ------------------------------------------------------------------------- | --------------- | ------------- | ------------------- |
| as_path | Used for transforming a string from a `ParentNode` to a validated `Path`. | `str \| Path`   | `str \| Path` | `str \| Path`       |
