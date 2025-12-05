![Banner](./assets/click-extended-todo-banner.png)

# Todo

## v1.0.0

### Documentation

- Add documentation for `@option` decorator (concatenated flags, new multiple flags, etc.)
- Add documentation for `@argument` decorator.

### Prompts

- `@confirm(prompt, truthy)`
- `@confirm_if(prompt, fn)`

### Select

- `@choice(*values)`

### Checks

- `@requires(*name)`
- `@conflicts(*names)`
- `@between(min, max, inclusive)`

### String

- `@expand_vars()`
- `@contains(*text)`
- `@strip(*chars)`
- `@lstrip(*chars)`
- `@rstrip(*chars)`
- `@truncate()`
- `@split(sep, maxsplit)`
- `@join(sep)`
- `@replace(old, new, count=-1)`
- `@regex(pattern)`
- `@url()`
- `@email()`
- `@ipv4()`
- `@ipv6()`
- `@port()`
- `@slugify()`
- `@remove_prefix(prefix)`
- `@remove_suffix(suffix)`

### Path

- `@basename()`
- `@dirname()`
- `@now(tz)` (Parent)

### Numerical

- `@divisible_by(n)`
- `@normalize(min, max)`
- `@clamp(min, max)`
- `@minimum(n)`
- `@maximum(n)`
- `@round(decimals)`
- `@absolute()`
- `@positive()`
- `@negative()`
- `@add(n)`
- `@subtract(n)`
- `@multiply(n)`
- `@divide(n)`
- `@power(n)`
- `@sqrt()`
- `@floor()`
- `@ceil()`
- `@modulo(n)`
- `@convert_time(from_unit, to_unit)`
- `@convert_temperature(from_unit, to_unit)`
- `@convert_weight(from_unit, to_unit)`
- `@convert_bytes(from_unit, to_unit)`
- `@convert_distance(from_unit, to_unit)`
- `@convert_speed(from_unit, to_unit)`
- `@convert_volume(from_unit, to_unit)`
- `@convert_area(from_unit, to_unit)`
- `@convert_pressure(from_unit, to_unit)`
- `@convert_energy(from_unit, to_unit)`
- `@convert_power(from_unit, to_unit)`
- `@convert_angle(from_unit, to_unit)`
