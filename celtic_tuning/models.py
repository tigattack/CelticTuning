"""Data models for celtic_tuning"""


from bs4 import BeautifulSoup
from pydantic import BaseModel, Field, field_validator

from .enums import PowerUnits, TorqueUnits


class PowerDetail(BaseModel):
    power_stock: int
    power_mapped: int
    power_diff: int
    torque_stock: int
    torque_mapped: int
    torque_diff: int
    power_unit: str
    torque_unit: str
    remap_chart_url: str

    @field_validator("power_unit", mode="before")
    @classmethod
    def validate_power_unit(cls, value: str | PowerUnits) -> str:
        if isinstance(value, str):
            value = PowerUnits(value)
        return value.value

    @field_validator("torque_unit", mode="before")
    @classmethod
    def validate_torque_unit(cls, value: str | TorqueUnits) -> str:
        if isinstance(value, str):
            value = TorqueUnits(value)
        return value.value

    @property
    def power_diff_pct(self) -> int:
        return round((self.power_diff / self.power_stock) * 100)

    @property
    def torque_diff_pct(self) -> int:
        return round((self.torque_diff / self.torque_stock) * 100)


class VehicleDetail(BaseModel):
    ecu_type: str
    displacement: int
    displacement_unit: str
    engine_variant: str
    fuel: str
    model: str
    year: int

    @property
    def displacement_formatted(self) -> str:
        return " ".join([str(self.displacement), self.displacement_unit])


class CelticData(BaseModel):
    power_detail: PowerDetail
    vehicle_detail: VehicleDetail
    vehicle_title: str
    result_url: str

    @property
    def pretty_printed(self) -> str:
        max_key_length = 0
        vehicle_detail_pretty = ""
        for key in self.vehicle_detail:
            max_key_length = max(len(key), max_key_length)

        for key, value in self.vehicle_detail:
            key_pretty = key.replace("_", " ").title()
            spaces = max_key_length - len(key_pretty)
            vehicle_detail_pretty += f'{key_pretty}: {" " * spaces}{value}\n'
        vehicle_detail_pretty = vehicle_detail_pretty.rstrip("\n")

        return (
            f"Found vehicle: {self.vehicle_title}\n\n"
            + "== VEHICLE DATA ==\n"
            + f"{vehicle_detail_pretty}\n\n"
            + "== REMAP DATA ==\n"
            + f"Stock power:  {self.power_detail.power_stock}\n"
            + f"Mapped power: {self.power_detail.power_mapped}\n\n"
            + f"Stock torque:  {self.power_detail.torque_stock}\n"
            + f"Mapped torque: {self.power_detail.torque_mapped}\n\n"
            + f"Power increase:  {self.power_detail.power_diff}\n"
            + f"Torque increase: {self.power_detail.torque_diff}\n\n"
            + f"Result URL: {self.result_url}\n"
            + f"Chart URL: {self.power_detail.remap_chart_url}"
        )


# TODO: implement something to actually use these cause I cba at the moment.
class CelticTuneStage(BaseModel):
    title: str
    url: str


class CelticTuneStages(BaseModel):
    stages: list[CelticTuneStage] = Field(default_factory=list)

    @classmethod
    def from_soup(cls, soup: BeautifulSoup) -> "CelticTuneStages":
        return cls(
            stages=[
                CelticTuneStage(title=stage.text, url=stage["href"])
                for stage in soup.find("div", id="ctvc_stageButtons").find_all("a")  # type: ignore
            ]
        )
