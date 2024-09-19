from typing import Literal

def bhp_to_kw(bhp: int) -> int:
    """Convert BHP to kW"""
    return round(bhp * 0.745699872)

def bhp_to_ps(bhp: int) -> int:
    """Convert BHP to PS"""
    return round(bhp * 1.01387)

def lb_ft_to_nm(lb_ft: int) -> int:
    """Convert lb/ft to Nm"""
    return round(lb_ft * 1.3558179483)

def convert_power_unit(
    value: int | float, from_unit: Literal["kW", "BHP", "PS"], to_unit: Literal["kW", "BHP", "PS"]
) -> int:
    """Convert power units"""
    unit = to_unit.lower()

    if from_unit == to_unit:
        return(int(value))

    if unit == "kw":
        return bhp_to_kw(int(value))

    if unit == "ps":
        return bhp_to_ps(int(value))

    raise ValueError(f"Cannot convert {from_unit} to {to_unit}")

def convert_torque_unit(value: int | float, from_unit: Literal["Nm", "lb/ft"], to_unit: Literal["Nm", "lb/ft"]) -> int:
    """Convert torque units"""
    unit = to_unit.lower()

    if from_unit == to_unit:
        return(int(value))

    if unit == "nm":
        return lb_ft_to_nm(int(value))

    raise ValueError(f"Cannot convert {from_unit} to {to_unit}")
