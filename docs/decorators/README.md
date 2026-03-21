![Banner](../../assets/click-extended-documentation-banner.png)

# Decorators

Pre-built decorators available from `click_extended.decorators`. They are split into categories based on their purpose.

All decorators are [ChildNodes](../core/CHILD_NODE.md) unless otherwise noted. ChildNodes must be placed **after** a parent (`@argument`, `@option`, `@env`, etc.) and are processed top-to-bottom.

## Categories

| Category                    | Import                      | Description                                                             |
| --------------------------- | --------------------------- | ----------------------------------------------------------------------- |
| [Check](./CHECK.md)         | `click_extended.decorators` | Validate string formats, numeric constraints, and inter-parameter rules |
| [Compare](./COMPARE.md)     | `click_extended.decorators` | Compare values against thresholds or ranges                             |
| [Convert](./CONVERT.md)     | `click_extended.decorators` | Convert numeric values between physical units                           |
| [Load](./LOAD.md)           | `click_extended.decorators` | Load file contents from a `pathlib.Path` value                          |
| [Math](./MATH.md)           | `click_extended.decorators` | Apply arithmetic and mathematical transformations                       |
| [Misc](./MISC.md)           | `click_extended.decorators` | Defaults, observation, confirmation, error handling, and more           |
| [Random](./RANDOM.md)       | `click_extended.decorators` | Generate random values as parameter sources                             |
| [Transform](./TRANSFORM.md) | `click_extended.decorators` | Transform strings: case, path, type conversion, and more                |

## Quick Reference

### Check

| Decorator                      | Supports         | Description                                          |
| ------------------------------ | ---------------- | ---------------------------------------------------- |
| `conflicts(*names)`            | `any`, `tag`     | Raise if conflicting parameters are also provided    |
| `contains(*text, all)`         | `str`            | Check that the string contains one or all substrings |
| `dependencies(*names)`         | `ValidationNode` | Ensure mutual dependencies between parameters        |
| `divisible_by(n)`              | `int`, `float`   | Check divisibility                                   |
| `ends_with(*text)`             | `str`            | Check that the string ends with a suffix             |
| `exclusive(*names)`            | `ValidationNode` | Enforce mutual exclusivity between parameters        |
| `falsy()`                      | `any`            | Raise if the value is truthy                         |
| `is_email()`                   | `str`            | Validate email address format                        |
| `is_hex_color()`               | `str`            | Validate hex color code                              |
| `is_hostname()`                | `str`            | Validate hostname format                             |
| `is_ipv4()`                    | `str`            | Validate IPv4 address                                |
| `is_ipv6()`                    | `str`            | Validate IPv6 address                                |
| `is_json()`                    | `str`            | Validate JSON string                                 |
| `is_mac_address()`             | `str`            | Validate MAC address                                 |
| `is_negative()`                | `int`, `float`   | Raise if value is not negative                       |
| `is_non_zero()`                | `int`, `float`   | Raise if value is zero                               |
| `is_numeric()`                 | `str`            | Raise if string is not numeric                       |
| `is_port()`                    | `int`            | Check value is a valid port (1–65535)                |
| `is_positive()`                | `int`, `float`   | Raise if value is not positive                       |
| `is_url(schemes, require_tld)` | `str`            | Validate URL format                                  |
| `is_uuid()`                    | `str`            | Validate UUID format                                 |
| `length(min, max)`             | `str`            | Check string length bounds                           |
| `not_empty()`                  | `str`            | Raise if string is empty                             |
| `regex(*patterns, flags)`      | `str`            | Validate against regular expression(s)               |
| `requires(*names)`             | `any`, `tag`     | Raise if required sibling parameters are missing     |
| `starts_with(*text)`           | `str`            | Check that the string starts with a prefix           |
| `truthy()`                     | `any`            | Raise if the value is falsy                          |

### Compare

| Decorator                            | Supports                                              | Description                                  |
| ------------------------------------ | ----------------------------------------------------- | -------------------------------------------- |
| `at_least(n)`                        | `int`, `float`                                        | Raise if value < n                           |
| `at_most(n)`                         | `int`, `float`                                        | Raise if value > n                           |
| `between(lower, upper, inclusive)`   | `int`, `float`, `date`, `time`, `datetime`            | Raise if value is outside bounds             |
| `greater_than(threshold, inclusive)` | `int`, `float`, `Decimal`, `datetime`, `date`, `time` | Raise if value is not greater than threshold |
| `less_than(threshold, inclusive)`    | `int`, `float`, `Decimal`, `datetime`, `date`, `time` | Raise if value is not less than threshold    |

### Convert

| Decorator                                 | Supports       | Description                       |
| ----------------------------------------- | -------------- | --------------------------------- |
| `convert_angle(from_unit, to_unit)`       | `int`, `float` | Convert between angle units       |
| `convert_area(from_unit, to_unit)`        | `int`, `float` | Convert between area units        |
| `convert_bits(from_unit, to_unit)`        | `int`, `float` | Convert between data size units   |
| `convert_distance(from_unit, to_unit)`    | `int`, `float` | Convert between distance units    |
| `convert_energy(from_unit, to_unit)`      | `int`, `float` | Convert between energy units      |
| `convert_power(from_unit, to_unit)`       | `int`, `float` | Convert between power units       |
| `convert_pressure(from_unit, to_unit)`    | `int`, `float` | Convert between pressure units    |
| `convert_speed(from_unit, to_unit)`       | `int`, `float` | Convert between speed units       |
| `convert_temperature(from_unit, to_unit)` | `int`, `float` | Convert between temperature units |
| `convert_time(from_unit, to_unit)`        | `int`, `float` | Convert between time units        |
| `convert_volume(from_unit, to_unit)`      | `int`, `float` | Convert between volume units      |
| `convert_weight(from_unit, to_unit)`      | `int`, `float` | Convert between weight units      |

### Load

| Decorator                     | Supports       | Description             |
| ----------------------------- | -------------- | ----------------------- |
| `load_csv(...)`               | `pathlib.Path` | Load CSV file contents  |
| `load_json(encoding, strict)` | `pathlib.Path` | Load JSON file contents |
| `load_toml()`                 | `pathlib.Path` | Load TOML file contents |
| `load_yaml(encoding, loader)` | `pathlib.Path` | Load YAML file contents |

### Math

| Decorator                                       | Supports              | Description                    |
| ----------------------------------------------- | --------------------- | ------------------------------ |
| `absolute()`                                    | `int`, `float`        | Return absolute value          |
| `add(n)`                                        | `int`, `float`, `str` | Add n to the value             |
| `ceil()`                                        | `int`, `float`        | Round up to nearest integer    |
| `clamp(min_val, max_val)`                       | `int`, `float`        | Clamp value to range           |
| `divide(n)`                                     | `int`, `float`        | Divide value by n              |
| `floor()`                                       | `int`, `float`        | Round down to nearest integer  |
| `maximum(max_val)`                              | `int`, `float`        | Cap value at a maximum         |
| `minimum(min_val)`                              | `int`, `float`        | Floor value at a minimum       |
| `modulo(n)`                                     | `int`, `float`        | Return value modulo n          |
| `multiply(n)`                                   | `int`, `float`        | Multiply value by n            |
| `normalize(min_val, max_val, new_min, new_max)` | `int`, `float`        | Normalize value within a range |
| `power(n)`                                      | `int`, `float`        | Raise value to the power n     |
| `rounded(digits)`                               | `int`, `float`        | Round to n decimal places      |
| `sqrt()`                                        | `int`, `float`        | Return square root             |
| `subtract(n)`                                   | `int`, `float`        | Subtract n from value          |
| `to_percent()`                                  | `int`, `float`        | Multiply by 100                |

### Misc

| Decorator                                   | Supports              | Description                                          |
| ------------------------------------------- | --------------------- | ---------------------------------------------------- |
| `catch(*exc_types, handler, reraise)`       | `ValidationNode`      | Catch exceptions from the command                    |
| `choice(*values, case_sensitive)`           | `str`, `int`, `float` | Validate value is one of the allowed choices         |
| `confirm_if(prompt, fn, truthy)`            | `any`                 | Prompt for confirmation based on a predicate         |
| `default(from_value, from_env, from_param)` | `any`                 | Set a default when no value was provided             |
| `deprecated(new, since, removed_in)`        | `any`                 | Print a deprecation warning when parameter is used   |
| `experimental(message)`                     | `any`                 | Print an experimental warning when parameter is used |
| `now(name, tz)`                             | `ParentNode`          | Inject the current datetime                          |
| `observe(handler)`                          | `any`                 | Observe a value without modifying it                 |

### Random

All random decorators are `ParentNode` type and take a `name` parameter.

| Decorator                                                                   | Returns     | Description                           |
| --------------------------------------------------------------------------- | ----------- | ------------------------------------- |
| `random_bool(name, weight, seed)`                                           | `bool`      | Generate a random boolean             |
| `random_choice(name, iterable, weights, seed)`                              | varies      | Pick a random element from a sequence |
| `random_datetime(name, start_date, end_date, timezone, seed)`               | `datetime`  | Generate a random datetime            |
| `random_float(name, min_value, max_value, decimals, seed)`                  | `float`     | Generate a random float               |
| `random_integer(name, min_value, max_value, seed)`                          | `int`       | Generate a random integer             |
| `random_prime(name, k, seed)`                                               | `int`       | Generate a random prime number        |
| `random_string(name, length, lowercase, uppercase, numbers, symbols, seed)` | `str`       | Generate a random string              |
| `random_uuid(name, version, namespace, uuid_name, seed)`                    | `uuid.UUID` | Generate a random UUID                |

### Transform

| Decorator                   | Supports              | Description                                |
| --------------------------- | --------------------- | ------------------------------------------ |
| `add_prefix(prefix, sep)`   | `str`                 | Prepend a prefix to the string             |
| `add_suffix(suffix, sep)`   | `str`                 | Append a suffix to the string              |
| `apply(fn)`                 | `any`                 | Apply an arbitrary function to the value   |
| `basename()`                | `str`, `Path`         | Return the final component of a path       |
| `dirname()`                 | `str`, `Path`         | Return the directory component of a path   |
| `expand_vars()`             | `str`                 | Expand environment variables in the string |
| `lstrip(chars)`             | `str`                 | Strip characters from the left             |
| `remove_prefix(prefix)`     | `str`                 | Remove a prefix from the string            |
| `remove_suffix(suffix)`     | `str`                 | Remove a suffix from the string            |
| `replace(old, new, count)`  | `str`                 | Replace occurrences in the string          |
| `rstrip(chars)`             | `str`                 | Strip characters from the right            |
| `slugify(**kwargs)`         | `str`                 | Convert to URL-friendly slug               |
| `split(sep, maxsplit)`      | `str`                 | Split string into a list                   |
| `strip(chars)`              | `str`                 | Strip characters from both ends            |
| `to_camel_case()`           | `str`                 | Convert to camelCase                       |
| `to_date(*formats)`         | `str`                 | Parse string to `datetime.date`            |
| `to_datetime(*formats, tz)` | `str`                 | Parse string to `datetime.datetime`        |
| `to_decimal()`              | `str`, `int`, `float` | Convert to `decimal.Decimal`               |
| `to_directory(...)`         | `str`                 | Convert and validate path as directory     |
| `to_dot_case()`             | `str`                 | Convert to dot.case                        |
| `to_file(...)`              | `str`                 | Convert and validate path as file          |
| `to_flat_case()`            | `str`                 | Convert to flatcase                        |
| `to_kebab_case()`           | `str`                 | Convert to kebab-case                      |
| `to_lower_case()`           | `str`                 | Convert to lowercase                       |
| `to_meme_case()`            | `str`                 | Convert to mEmE cAsE                       |
| `to_pascal_case()`          | `str`                 | Convert to PascalCase                      |
| `to_path(...)`              | `str`                 | Convert and validate as `pathlib.Path`     |
| `to_path_case()`            | `str`                 | Convert to path/case                       |
| `to_screaming_snake_case()` | `str`                 | Convert to SCREAMING_SNAKE_CASE            |
| `to_snake_case()`           | `str`                 | Convert to snake_case                      |
| `to_string()`               | `any`                 | Convert value to string                    |
| `to_symlink(...)`           | `str`                 | Convert and validate path as symlink       |
| `to_time(*formats)`         | `str`                 | Parse string to `datetime.time`            |
| `to_timestamp(unit)`        | `datetime`, `date`    | Convert datetime to numeric timestamp      |
| `to_title_case()`           | `str`                 | Convert to Title Case                      |
| `to_train_case()`           | `str`                 | Convert to Train-Case                      |
| `to_upper_case()`           | `str`                 | Convert to UPPERCASE                       |
| `truncate(length, suffix)`  | `str`                 | Truncate string to a maximum length        |
