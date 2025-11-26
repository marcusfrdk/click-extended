![Banner](../../assets/click-extended-documentation-banner.png)

# Migrating From Click

If you have used Click before, migrating to `click-extended` is straight-forward. However, there are some things which are optionionated, such as the structure and how to work with data.

## Concepts

These are concepts `click` implement which are implemented in the `click-extended` library and are used as a direct replacement.

| `click`                      | `click-extended` |
| ---------------------------- | ---------------- |
| `@click.command`             | `@command`       |
| `@click.group`               | `@group`         |
| `@click.option`              | `@option`        |
| `@click.argument`            | `@argument`      |
| `@click.password_option`     |                  |
| `@click.confirmation_option` |                  |
| `@click.version_option`      |                  |
| `@click.help_option`         |                  |

## Types

Types are used to determine what `click` converts the value to (for the `@argument` and `@option` parent decorators).

| `click`             | `click-extended`                                                          |
| ------------------- | ------------------------------------------------------------------------- |
| `click.STRING`      | `str`                                                                     |
| `click.INT`         | `int`                                                                     |
| `click.FLOAT`       | `float`                                                                   |
| `click.bool`        | `bool`                                                                    |
| `click.UUID`        | Use the `@as_uuid` child decorator.                                       |
| `click.UNPROCESSED` |                                                                           |
| `click.File`        | Use the `@as_path` child decorator.                                       |
| `click.Choice`      | Use the `@choice` child decorator.                                        |
| `click.IntRange`    | Use the `@in_range` child decorator.                                      |
| `click.FloatRange`  | Use the `@in_range` child decorator.                                      |
| `click.DateTime`    | Use the `@as_datetime` child decorator.                                   |
| `click.Tuple`       | Use the `nargs` parameter for `@argument` or `@option` parent decorators. |
| `click.ParamType`   |                                                                           |

## Errors

This library is unopinionated about exceptions, as all non-critical exceptions (`KeyboardInterrupt`, `SystemExit`, etc.) will be caught and formatted in a custom format, meaning all exception in `click` will be handled.

## Examples

Examples coming soon...
