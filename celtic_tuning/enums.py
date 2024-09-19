"""Enums for celtic_tuning"""

from enum import Enum


class PowerUnits(Enum):
    BHP = "BHP"
    KW = "kW"
    PS = "PS"

    @classmethod
    def bhp_to_kw(cls, bhp: int) -> int:
        """Convert BHP to kW. Returns closest integer."""
        return round(bhp * 0.745699872)

    @classmethod
    def bhp_to_ps(cls, bhp: int) -> int:
        """Convert BHP to PS. Returns closest integer."""
        return round(bhp * 1.01387)


class TorqueUnits(Enum):
    NM = "Nm"
    LB_FT = "lb/ft"

    @classmethod
    def lbft_to_nm(cls, lb_ft: int) -> int:
        """Convert lb/ft to Nm"""
        return round(lb_ft * 1.3558179483)


class CelticDefaultUnits(Enum):
    """Default"""

    POWER = PowerUnits.BHP.value
    TORQUE = TorqueUnits.LB_FT.value
