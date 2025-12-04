![Banner](./assets/click-extended-todo-banner.png)

# Todo

## v1.0.0

- `@to_set()`
- `@to_list()`
- `@to_tuple()`
- `@to_timestamp(length)`
- `@to_datetime(formats)`
- `@to_date(formats)`
- `@to_time(formats)`
- `@load_toml(encoding)`
- `@load_csv(dialect, delimiter, had_header, as_dict, encoding, skip_empty)`
- `@expand_vars()`
- `@confirm(prompt, truthy)`
- `@confirm_if(prompt, fn)`
- `@requires(*name)`
- `@conflicts(*names)`
- `@in_range(min, max, inclusive=True)` (supports int, float, datetime)
- `@more_than(value, inclusive)`
- `@less_than(value, inclusive)`
- `@min_length(n)`
- `@max_length(n)`
- `@not_empty(n)`
- `@flatten()`
- `@contains(*text, all_of, none_of)`
- `@starts_with(*text)`
- `@ends_with(*text)`
- `@divisible_by(n)`
- `@choice(*values)`
- `@strip(chars)`
- `@split(sep, maxsplit)`
- `@join(sep)`
- `@replace(old, new, count=-1)`
- `@regex(pattern)`
- `@add_timezone(tz)`
- `@add_prefix(text)`
- `@add_suffix(text)`
- `@add_protocol(protocol)` (Add protocol if missing, e.g. google.com -> https://google.com)
- `@normalize(min, max)`
- `@standardize()`
- `@clamp(min, max)`
- `@sort(reverse)`
- `@unique()`
- `@url()`
- `@email()`
- `@ipv4()`
- `@ipv6()`
- `@port()`
- `@positive()`
- `@negative()`
- `@non_zero()`
