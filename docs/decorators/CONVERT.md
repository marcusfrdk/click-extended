![Banner](../../assets/click-extended-documentation-banner.png)

# Convert Decorators

Convert decorators transform numeric values between physical units. All are `ChildNode` type and must appear after a parent decorator. Each decorator accepts `from_unit` and `to_unit` parameters using the unit codes documented below.

All convert decorators support `int` and `float` input values.

## Table of Contents

- [convert\_angle](#convert_angle)
- [convert\_area](#convert_area)
- [convert\_bits](#convert_bits)
- [convert\_distance](#convert_distance)
- [convert\_energy](#convert_energy)
- [convert\_power](#convert_power)
- [convert\_pressure](#convert_pressure)
- [convert\_speed](#convert_speed)
- [convert\_temperature](#convert_temperature)
- [convert\_time](#convert_time)
- [convert\_volume](#convert_volume)
- [convert\_weight](#convert_weight)

---

## convert\_angle

```python
convert_angle(from_unit: str, to_unit: str) -> Decorator
```

| Unit | Description |
| ---- | ----------- |
| `deg` | Degree |
| `rad` | Radian |
| `grad` | Gradian |
| `turn` | Full turn |
| `arcmin` | Arcminute |
| `arcsec` | Arcsecond |
| `rev` | Revolution |
| `mil` | NATO angular mil |

```python
@option("angle", type=float)
@convert_angle("deg", "rad")
```

---

## convert\_area

```python
convert_area(from_unit: str, to_unit: str) -> Decorator
```

| Unit | Description |
| ---- | ----------- |
| `mm2` | Square millimeter |
| `cm2` | Square centimeter |
| `dm2` | Square decimeter |
| `m2` | Square meter |
| `a` | Are (100 m²) |
| `ha` | Hectare (10,000 m²) |
| `km2` | Square kilometer |
| `in2` | Square inch |
| `ft2` | Square foot |
| `yd2` | Square yard |
| `mi2` | Square mile |
| `acre` | Acre |
| `rood` | Rood (¼ acre) |
| `perch` | Perch (1/160 acre) |
| `ang2` | Square ångström |
| `tunnland` | Historical Swedish area unit (~4,937 m²) |

---

## convert\_bits

```python
convert_bits(from_unit: str, to_unit: str) -> Decorator
```

**Decimal byte units:** `B`, `kB`, `MB`, `GB`, `TB`, `PB`, `EB`, `ZB`, `YB`, `RB`, `QB`

**Binary (IEC) byte units:** `KiB`, `MiB`, `GiB`, `TiB`, `PiB`, `EiB`, `ZiB`, `YiB`

**Decimal bit units:** `b`, `kb`, `Mb`, `Gb`, `Tb`, `Pb`, `Eb`, `Zb`, `Yb`, `Rb`, `Qb`

**Binary (IEC) bit units:** `Kib`, `Mib`, `Gib`, `Tib`, `Pib`, `Eib`, `Zib`, `Yib`

```python
@argument("size", type=float)
@convert_bits("MB", "GiB")
```

---

## convert\_distance

```python
convert_distance(from_unit: str, to_unit: str) -> Decorator
```

| Unit | Description |
| ---- | ----------- |
| `mm` | Millimeter |
| `cm` | Centimeter |
| `dm` | Decimeter |
| `m` | Meter |
| `km` | Kilometer |
| `in` | Inch |
| `ft` | Foot |
| `yd` | Yard |
| `mi` | Mile |
| `nmi` | Nautical mile |
| `nm` | Nanometer |
| `us` | Micrometer |
| `AU` | Astronomical Unit |
| `ly` | Light-year |
| `pc` | Parsec |
| `ang` | Ångström |
| `mil` | Swedish mile (10 km) |
| `pm`, `fm`, `am`, `zm`, `ym`, `Rm`, `Qm` | SI prefix meters |

---

## convert\_energy

```python
convert_energy(from_unit: str, to_unit: str) -> Decorator
```

| Unit | Description |
| ---- | ----------- |
| `J`, `kJ`, `MJ`, `GJ`, `TJ` | Joules (SI prefixes) |
| `Wh`, `kWh`, `MWh`, `GWh`, `TWh` | Watt-hours |
| `cal`, `kcal` | Calories / kilocalories |
| `eV`, `keV`, `MeV`, `GeV`, `TeV` | Electron volts |
| `ftlb` | Foot-pound |
| `inlb` | Inch-pound |
| `Btu` | British thermal unit |
| `therm` | Therm |
| `erg` | Erg |
| `ktTNT` | Kiloton of TNT |
| `MtTNT` | Megaton of TNT |

---

## convert\_power

```python
convert_power(from_unit: str, to_unit: str) -> Decorator
```

| Unit | Description |
| ---- | ----------- |
| `W`, `kW`, `MW`, `GW`, `TW` | Watts (SI prefixes) |
| `hp` | Horsepower |
| `hpM` | Metric horsepower |
| `dBW` | Decibel-watt |
| `dBm` | Decibel-milliwatt |
| `Btuh` | BTU per hour |
| `Btus` | BTU per second |
| `ftlbs` | Foot-pounds per second |
| `tonref` | Ton of refrigeration |

---

## convert\_pressure

```python
convert_pressure(from_unit: str, to_unit: str) -> Decorator
```

| Unit | Description |
| ---- | ----------- |
| `Pa`, `kPa`, `MPa`, `GPa` | Pascals (SI prefixes) |
| `bar`, `mbar`, `hPa` | Bar / millibar / hectopascal |
| `psi`, `ksi`, `psf` | Pounds per square inch/foot |
| `mmHg`, `inHg` | Mercury column |
| `mmH2O`, `inH2O` | Water column |
| `atm` | Standard atmosphere |
| `at` | Technical atmosphere |
| `torr` | Torr |
| `Ba` | Barye |

---

## convert\_speed

```python
convert_speed(from_unit: str, to_unit: str) -> Decorator
```

| Unit | Description |
| ---- | ----------- |
| `mps` | Meters per second |
| `kmh` | Kilometers per hour |
| `mph` | Miles per hour |
| `fps` | Feet per second |
| `ftmin` | Feet per minute |
| `inps` | Inches per second |
| `kn`, `kt` | Knots |
| `mach` | Mach number |
| `c` | Fraction of speed of light |
| `kmps` | Kilometers per second |
| `cmps` | Centimeters per second |
| `mmps` | Millimeters per second |
| `auday` | AU per day |
| `kmday` | Kilometers per day |
| `pcyr` | Parsecs per year |

---

## convert\_temperature

```python
convert_temperature(from_unit: str, to_unit: str) -> Decorator
```

| Unit | Description |
| ---- | ----------- |
| `C` | Celsius |
| `F` | Fahrenheit |
| `K` | Kelvin |
| `R` | Rankine |
| `Re` | Réaumur |
| `De` | Delisle |

```python
@option("temp", type=float)
@convert_temperature("C", "F")
```

---

## convert\_time

```python
convert_time(from_unit: str, to_unit: str) -> Decorator
```

| Unit | Description |
| ---- | ----------- |
| `ns` | Nanoseconds |
| `us` | Microseconds |
| `ms` | Milliseconds |
| `s` | Seconds |
| `m` | Minutes |
| `h` | Hours |
| `d` | Days |
| `w` | Weeks |
| `M` | Months |
| `y` | Years |

Also supports `str` input (numeric string).

---

## convert\_volume

```python
convert_volume(from_unit: str, to_unit: str) -> Decorator
```

| Unit | Description |
| ---- | ----------- |
| `mm3`, `cm3`, `m3`, `km3` | Cubic metric |
| `mL`, `cL`, `dL`, `L`, `hL`, `kL`, `ML` | Litres (SI prefixes) |
| `in3`, `ft3`, `yd3` | Cubic imperial |
| `floz`, `cup`, `pt`, `qt`, `gal` | US liquid |
| `imp_floz`, `imp_pt`, `imp_qt`, `imp_gal` | Imperial |
| `bbl` | Barrel |
| `cc` | Cubic centimeter |
| `tsp`, `tbsp` | Teaspoon / tablespoon |
| `gill`, `imp_gill` | Gill |
| `drop` | Drop |
| `dry_pt`, `dry_qt`, `dry_gal` | US dry |
| `pk`, `bu` | Peck / bushel |
| `firkin`, `kilderkin` | Historical barrel fractions |
| `krm`, `tsk`, `msk` | Swedish cooking measures |

---

## convert\_weight

```python
convert_weight(
    from_unit: str,
    to_unit: str,
    gravity: float = 9.80665,
) -> Decorator
```

| Unit | Description |
| ---- | ----------- |
| `ug`, `mg`, `g`, `kg`, `t` | Metric mass |
| `lb` | Pound |
| `oz` | Ounce |
| `st` | Stone |
| `ct` | Carat |
| `amu` | Atomic mass unit |
| `n`, `kn` | Newton / kilonewton (force) |
| `lbf`, `ozf`, `kgf` | Pound/ounce/kilogram-force |
| `dyn` | Dyne |
| `slg` | Slug |

The `gravity` parameter (default `9.80665 m/s²`) is used for force↔mass conversions.
