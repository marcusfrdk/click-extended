![Banner](../../assets/click-extended-documentation-banner.png)

# Migrating From Click

If you have used Click before, migrating to `click-extended` is straight-forward. However, there are some things which are opinionated, such as the structure and how to work with data.

## Concepts

These are concepts `click` implement which are implemented in the `click-extended` library and are used as a direct replacement.

| `click`                      | `click-extended`     |
| ---------------------------- | -------------------- |
| `@click.command`             | `@command`           |
| `@click.group`               | `@group`             |
| `@click.option`              | `@option`            |
| `@click.argument`            | `@argument`          |
| `@click.password_option`     | No direct equivalent |
| `@click.confirmation_option` | No direct equivalent |
| `@click.version_option`      | No direct equivalent |
| `@click.help_option`         | No direct equivalent |

## Types

Types are used to determine what `click` converts the value to (for the `@argument` and `@option` parent decorators).

| `click`             | `click-extended`                                                          |
| ------------------- | ------------------------------------------------------------------------- |
| `click.STRING`      | `str`                                                                     |
| `click.INT`         | `int`                                                                     |
| `click.FLOAT`       | `float`                                                                   |
| `click.BOOL`        | `bool`                                                                    |
| `click.UUID`        | Use the `@to_uuid` child decorator.                                       |
| `click.UNPROCESSED` | No direct equivalent                                                      |
| `click.File`        | Use the `@to_path` child decorator.                                       |
| `click.Choice`      | Use the `@choice` child decorator.                                        |
| `click.IntRange`    | Use the `@between` child decorator.                                       |
| `click.FloatRange`  | Use the `@between` child decorator.                                       |
| `click.DateTime`    | Use the `@to_datetime` child decorator.                                   |
| `click.Tuple`       | Use the `nargs` parameter for `@argument` or `@option` parent decorators. |
| `click.ParamType`   | No direct equivalent                                                      |

## Errors

This library is unopinionated about exceptions, as all non-critical exceptions (`KeyboardInterrupt`, `SystemExit`, etc.) will be caught and formatted in a custom format, meaning all exception in `click` will be handled.
