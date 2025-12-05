![Banner](./assets/click-extended-todo-banner.png)

# Todo

## v1.0.0

- Add documentation for `@option` decorator (concatenated flags, new multiple flags, etc.)
- Add documentation for `@argument` decorator.
- `@expand_vars()`
- `@confirm(prompt, truthy)`
- `@confirm_if(prompt, fn)`
- `@requires(*name)`
- `@conflicts(*names)`
- `@in_range(min, max, inclusive=True)` (supports int, float, datetime)
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
