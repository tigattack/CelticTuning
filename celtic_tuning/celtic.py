"""Get remap data from Celtic Tuning"""

import requests
from bs4 import BeautifulSoup, Tag

from . import utils
from .enums import CelticDefaultUnits, PowerUnits, TorqueUnits
from .models import CelticData, PowerDetail, VehicleDetail

# Usage notes:
# Only supports returning data for a "stage 1" map.
# For vehicles with supported "stage 2" maps, "economy" maps, etc., only the stage 1 result
# will be returned.
# This isn't a technical limitation, simply a 'lack of fucks given' limitation on my part.
# There is a partial implementation of this in models.py, it just needs to be actually used.


class Celtic:
    """Get vehicle information and remap estimates from Celtic Tuning."""

    def __init__(
        self,
        vrn: str,
        power_unit: str = "BHP",
        torque_unit: str = "lb/ft",
    ) -> None:
        self.base_url = "https://www.celtictuning.co.uk"
        self.search_path = "/component/ctvc/search?dvla="

        # Normalise and validate power unit
        power_unit_normalised = utils.resolve_unit_case(power_unit, PowerUnits)
        if power_unit_normalised not in PowerUnits._value2member_map_:
            raise ValueError(f"Invalid power unit: {power_unit}. Must be one of {[unit.value for unit in PowerUnits]}")

        # Normalise and validate torque unit
        torque_unit_normalised = utils.resolve_unit_case(torque_unit, TorqueUnits)
        if torque_unit_normalised not in TorqueUnits._value2member_map_:
            raise ValueError(f"Invalid torque unit: {torque_unit}. Must be one of {[unit.value for unit in TorqueUnits]}")

        self.power_unit = power_unit_normalised
        self.torque_unit = torque_unit_normalised

        self.result_url, self.vehicle_page_content = self._scrape_vehicle_page(vrn)

    def _scrape_vehicle_page(self, vrn: str) -> tuple[str, BeautifulSoup]:
        """Scrape vehicle info page for given VRN. Returns result URL and BeautifulSoup object for full page content."""
        bad_vrn_message = (
            f"Unable to locate data for '{vrn.upper()}'. Either Celtic Tuning does "
            + "not offer a tune for this vehicle, or the registration is incorrect."
        )

        # Search for a VRN and return the vehicle info page URL
        search_url = self.base_url + self.search_path + vrn

        search_response = requests.get(search_url, allow_redirects=False, timeout=5)
        redirect_path = search_response.headers["Location"].replace(self.base_url, "")

        if redirect_path == "/component/ctvc/#t3-content":
            raise ValueError(bad_vrn_message)

        result_url = self.base_url + redirect_path

        # Get vehicle info page and return as BeautifulSoup object
        data_response = requests.get(result_url, timeout=5)
        page_content = BeautifulSoup(data_response.content, "html.parser")

        if "Please select variant" in page_content.text or page_content.find(class_="alert alert-error"):
            raise ValueError(bad_vrn_message)

        return result_url, page_content

    def get_all(self) -> CelticData:
        """Return all data"""
        remap_data = self.get_power_detail()
        vehicle_title = self.get_vehicle_title()
        vehicle_detail = self.get_vehicle_detail()

        return CelticData(
            power_detail=remap_data,
            vehicle_detail=vehicle_detail,
            vehicle_title=vehicle_title,
            result_url=self.result_url,
        )

    def get_power_detail(self) -> PowerDetail:
        """Return remap data"""
        map_data_divs = self.vehicle_page_content.find_all("div", class_="ctvc_gauge_text")

        result_texts = []
        for element in map_data_divs:
            element_text = element.find("h5")
            result_texts.append(element_text.text.strip())

        power_stock = utils.convert_power_unit(result_texts[0], CelticDefaultUnits.POWER.value, self.power_unit)
        power_tuned = utils.convert_power_unit(result_texts[1], CelticDefaultUnits.POWER.value, self.power_unit)
        power_diff = utils.convert_power_unit(result_texts[2], CelticDefaultUnits.POWER.value, self.power_unit)
        torque_stock = utils.convert_torque_unit(result_texts[3], CelticDefaultUnits.TORQUE.value, self.torque_unit)
        torque_tuned = utils.convert_torque_unit(result_texts[4], CelticDefaultUnits.TORQUE.value, self.torque_unit)
        torque_diff = utils.convert_torque_unit(result_texts[5], CelticDefaultUnits.TORQUE.value, self.torque_unit)

        dyno_chart_url = self.get_vehicle_dyno_chart_url(self.vehicle_page_content)

        return PowerDetail(
            power_stock=power_stock,
            power_tuned=power_tuned,
            power_diff=power_diff,
            torque_stock=torque_stock,
            torque_tuned=torque_tuned,
            torque_diff=torque_diff,
            power_unit=self.power_unit,
            torque_unit=self.torque_unit,
            dyno_chart_url=dyno_chart_url,
        )

    def get_vehicle_title(self) -> str:
        """Return vehicle title"""
        vehicle_title_element = self.vehicle_page_content.find(id="ctvc-title")
        return vehicle_title_element.text.strip().replace("\n", " ").replace("  ", "")  # type:ignore

    def get_vehicle_detail(self) -> VehicleDetail:
        """Return vehicle information table"""
        vehicle_data = {}
        vehicle_data_table = self.vehicle_page_content.find("ul", attrs={"class": "ctvs_list"})

        if isinstance(vehicle_data_table, Tag):
            rows = vehicle_data_table.find_all("li")
            for row in rows:
                row_text = row.text.strip().replace("\n", " ").replace("  ", "")
                row_text = row_text.split(":")
                row_key = row_text[0].replace(" ", "_").lower()
                row_value = row_text[1]
                vehicle_data.update({row_key: row_value})

            # Process transformations
            displacement, displacement_unit = vehicle_data.pop("engine_size").split(" ")
            vehicle_data["displacement"] = int(displacement)
            vehicle_data["displacement_unit"] = displacement_unit
            vehicle_data["engine_variant"] = vehicle_data.pop("variant")

            return VehicleDetail(**vehicle_data)
        raise ValueError("Vehicle data table is unexpected format")

    def get_vehicle_dyno_chart_url(self, vehicle_page: BeautifulSoup) -> str | None:
        """Return vehicle remap chart URL"""
        chart_btn = vehicle_page.select_one("a.ctvc_chart_btn")
        if chart_btn:
            chart_url = chart_btn["href"]
            return str(chart_url)
        return None
