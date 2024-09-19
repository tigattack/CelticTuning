"""Utils for celtic_tuning"""

from typing import LiteralString, Union

from .enums import PowerUnits, TorqueUnits


def convert_power_unit(value: int | float, from_unit: str, to_unit: str) -> int:
    """Convert power units"""
    unit = to_unit.lower()

    if from_unit == to_unit:
        return int(value)

    if unit == "kw":
        return PowerUnits.bhp_to_kw(int(value))

    if unit == "ps":
        return PowerUnits.bhp_to_ps(int(value))

    raise ValueError(f"Cannot convert {from_unit} to {to_unit}")


def convert_torque_unit(value: int | float, from_unit: str, to_unit: str) -> int:
    """Convert torque units"""
    unit = to_unit.lower()

    if from_unit == to_unit:
        return int(value)

    if unit == "nm":
        return TorqueUnits.lbft_to_nm(int(value))

    raise ValueError(f"Cannot convert {from_unit} to {to_unit}")


def resolve_unit_case(
    unit: str, enum_class: type[Union[PowerUnits, TorqueUnits]]
) -> LiteralString:
    """Returns the given power or torque unit string with correct case if found in `enum_class`."""
    unit = unit.lower()
    for enum_member in enum_class:
        if unit == enum_member.value.lower():
            return enum_member.value
    raise ValueError(
        f"Invalid unit for {enum_class.__name__}: {unit}. Must be one of {', '.join([unit.value for unit in enum_class])}"
    )
