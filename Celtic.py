"""Get remap data from Celtic Tuning"""

from enum import Enum
import requests
from bs4 import BeautifulSoup

# Usage notes:
# Only supports returning data for a "stage 1" map.
# For vehicles with supported "stage 2" maps, "economy" maps, etc., only the stage 1 result
#  will be returned.
# This isn't a technical limitation, simply a 'lack of fucks given' limitation on my part.

# Resources:
# https://realpython.com/beautiful-soup-web-scraper-python

# TODO: Get stages. Get text of 'a' elements in div id 'ctvc_stageButtons' for
# stage options, and get URL from element to be used when scraping.

# Stretch: Get remap chart. Chart URL is available from 'a' element with class 'ctvc_chart_btn'.

class CelticUnits(Enum):
    """Enums to be consumed by Celtic class"""
    POWER   = 'BHP'
    TORQUE  = 'lb/ft'

class Celtic:
    """Get vehicle information and remap estimates from Celtic Tuning."""
    def __init__(self, vrn: str):
        self.vrn = vrn
        self.is_bad_vrn = False

        bad_vrn_message = (
            f"Error: A vehicle with registration \"{self.vrn.upper()}\" could not be found.\n\n" +
            "Possible causes:\n" +
            "- Incorrect registration.\n" +
            "- Celtic Tuning does not offer a tune for this vehicle.\n" +
            "- Celtic Tuning could not be identify the vehicle based on the "
            "information provided by the DVLA."
        )

        base_url    = 'https://www.celtictuning.co.uk'
        search_path = '/component/ctvc/search?dvla='

        # Search for a VRN and return the vehicle info page URL
        search_url = base_url + search_path + vrn

        search_response = requests.get(
            search_url,
            allow_redirects=False,
            timeout=5
        )
        redirect_path = search_response.headers['Location']

        if redirect_path == '/component/ctvc/#t3-content':
            raise ValueError(bad_vrn_message)

        self.result_url = base_url + redirect_path

        # Get vehicle info page and return as BeautifulSoup object
        data_response = requests.get(
            self.result_url,
            timeout=5
        )
        self.vehicle_page_content = BeautifulSoup(data_response.content, "html.parser")

        if 'Please select variant' in self.vehicle_page_content.text:
            raise ValueError(bad_vrn_message)


    def get_remap_data(self) -> dict:
        """Parse remap data"""
        map_data_divs = self.vehicle_page_content.find_all("div", class_="ctvc_gauge_text")

        result_texts = []
        for element in map_data_divs:
            element_text = element.find("h5")
            result_texts.append(element_text.text.strip())

        remap_data = {}
        remap_data.update(
            {'power_stock': f"{result_texts[0]} {CelticUnits.POWER.value}"}
        )
        remap_data.update(
            {'power_mapped': f"{result_texts[1]} {CelticUnits.POWER.value}"}
        )
        remap_data.update(
            {'power_diff': f"{result_texts[2]} {CelticUnits.POWER.value}"}
        )
        remap_data.update(
            {'torque_stock': f"{result_texts[3]} {CelticUnits.TORQUE.value}"}
        )
        remap_data.update(
            {'torque_mapped': f"{result_texts[4]} {CelticUnits.TORQUE.value}"}
        )
        remap_data.update(
            {'torque_diff': f"{result_texts[5]} {CelticUnits.TORQUE.value}"}
        )

        return remap_data


    def get_vehicle_title(self) -> str:
        """Parse vehicle title"""
        vehicle_title_element = self.vehicle_page_content.find(id='ctvc-title')
        return vehicle_title_element.text.strip().replace('\n', ' ').replace('  ', '') # type:ignore


    def get_vehicle_detail(self) -> dict:
        """Parse vehicle information table"""
        vehicle_data = {}
        vehicle_data_table = self.vehicle_page_content.find('ul', attrs={'class':'ctvs_list'})

        rows = vehicle_data_table.find_all('li') # type: ignore
        for row in rows:
            row_text    = row.text.strip().replace('\n', ' ').replace('  ', '')
            row_text    = row_text.split(':')
            row_key     = row_text[0].replace(' ', '_').lower()
            row_value   = row_text[1]
            vehicle_data.update({row_key: row_value})

        return vehicle_data


    def get_all(self) -> dict:
        """Return dict of all data points"""
        remap_data      = self.get_remap_data()
        vehicle_title   = self.get_vehicle_title()
        vehicle_detail  = self.get_vehicle_detail()

        return {
            'remap_data':     remap_data,
            'vehicle_title':  vehicle_title,
            'vehicle_detail': vehicle_detail,
            'result_url':     self.result_url
        }


    def get_all_pretty(self) -> str:
        """Return all data as a multi-line string"""
        remap_data    = self.get_remap_data()
        vehicle_title = self.get_vehicle_title()
        vehicle_detail  = self.get_vehicle_detail()

        max_key_length = 0
        vehicle_detail_pretty = ''
        for key in vehicle_detail:
            if len(key) > max_key_length:
                max_key_length = len(key)

        for key,value in vehicle_detail.items():
            key_pretty = key.replace('_', ' ').title()
            spaces = max_key_length - len(key_pretty)
            vehicle_detail_pretty += f'{key_pretty}: {" " * spaces}{value}\n'
        vehicle_detail_pretty = vehicle_detail_pretty.rstrip('\n')

        pretty_info = (
            f"Found vehicle: {vehicle_title}\n\n" +
            "== VEHICLE DATA ==\n" +
            f"{vehicle_detail_pretty}\n\n" +
            "== REMAP DATA ==\n" +
            f"Stock power:  {remap_data['power_stock']}\n" +
            f"Mapped power: {remap_data['power_mapped']}\n\n" +
            f"Stock torque:  {remap_data['torque_stock']}\n" +
            f"Mapped torque: {remap_data['torque_mapped']}\n\n" +
            f"Power increase:  {remap_data['power_diff']}\n" +
            f"Torque increase: {remap_data['torque_diff']}\n\n" +
            f"Result URL: {self.result_url}"
        )

        return pretty_info
