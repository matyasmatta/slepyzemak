# This should be some simple code to get the POIs off OpenStreetMap
# Traces: ChatGPT

from geopy.geocoders import Nominatim
import json
import csv
from tqdm import tqdm
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from utils import Logger
from urllib.parse import urlparse, parse_qs
import re
import logging

class SeleniumMethods:
    def __init__(self, browser="Chrome"):
        logging.getLogger('selenium').setLevel(logging.ERROR)
        if browser == "Chrome":
            self.driver = self.chrome()
        else:
            error = "Unsupported browser passed into a Selenium method, please use Chrome."
            logger.write("error", error)
            raise NotImplementedError(error)
    
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_value, traceback):
        self.quit_driver()

    def chrome(self):
        # create runtime window
        options = Options()
        options.headless = True
        options.add_argument("--window-size=1920,1200")
        options.add_argument("--allow-mixed-content")
        options.add_argument('log-level=3')

        # since v0.0.2 no longer necessary to pass in chromedrive location, now it will install on its own! (about 8 MiB so no worries)
        try:
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
            return driver
        except Exception as e:
            error = f"The webdriver failed to initialise: {str(e)}"
            logger.write("error", error)
            raise ConnectionError(error)

    def mapy(self, place):
        try:
            # Returns coordinates in a tuple
            self.driver.get(f"https://mapy.cz/turisticka?q={place}")
            WebDriverWait(self.driver, 10).until(EC.url_contains("x"))

            current_url = self.driver.current_url
            self.driver.implicitly_wait(1)
            parsed_url = urlparse(current_url)
            query_params = parse_qs(parsed_url.query)

            x_coordinate = query_params.get('x')[0]
            y_coordinate = query_params.get('y')[0]

            return (float(y_coordinate), float(x_coordinate))
        except Exception as e:
            error = f"There was an error in the SeleniumMethods.mapy() module, raw as follows {e}"
            logger.write("error", error)
            raise Exception(error)
    
    def google_maps(self, place):
        self.driver.get(f"https://www.google.com/maps/place/{place}/")
        try:
            WebDriverWait(self.driver, 10).until(EC.url_contains("@"))
        except:
            error = "There was a timeout in the SeleniumMethods.google_maps() module."
            logger.write("error", error)
            raise TimeoutError(error)
        current_url = self.driver.current_url
        # Define a regular expression pattern to extract the coordinates
        pattern = r'@([-+]?\d+\.\d+),([-+]?\d+\.\d+)'

        # Use re.findall to find all occurrences of the pattern in the URL
        matches = re.findall(pattern, current_url)

        if matches:
            latitude, longitude = matches[0]
            return (float(latitude), float(longitude))
        else:
            print("Coordinates not found in the URL.")

    def quit_driver(self):
        self.driver.quit()
        


def process_csv(file_path):
    places_data = []

    def interpret_description(czech_description):
        mapping = {
            'řeka': ['river', 'waterway'],
            'jezero': ['lake', 'water'],
            'přehrada': ['reservoir', 'water', 'dam'],
            'rybník': ['reservoir', 'water', 'lake'],
            'hora': ['mountain', 'peak', 'Hora'],
            'pohoří': ['topo', 'range', 'mountain_range', 'Pohoří', 'Hora']
            # Add more mappings as needed
        }
        result = mapping.get(czech_description, [])
        result.insert(0, czech_description)  # Insert original value at the beginning
        return result

    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            if len(row) == 2:
                place_name = row[0].strip()
                description = interpret_description(row[1].strip())
                places_data.append({"place_name": place_name, "description": description})

    return places_data

def openstreetmap_get(place_name, permissible_types=["river"]):
    geolocator = Nominatim(user_agent="convert.py")
    locations = geolocator.geocode(place_name, exactly_one=False, country_codes="cz")

    new_locations = list()
    try:
        for item in locations:
            if item.raw["type"] in permissible_types:
                new_locations.append(item)
            else:
                pass
    except:
        return None
    
    if new_locations:
        return new_locations
    else:
        return None

def mapycz_get(place_name, permissible_types):
    """Fetches the coordinates of a place from the mapy.cz REST API.

    Args:
        place_name: The name of the place.

    Returns:
        A tuple of (latitude, longitude) or None if the place is not found.
    """
    API_KEY = "GjRkRPpn-ganixbQqKBQq-tSLtCJ52woaGrg698ZwMI"
    url = f"https://api.mapy.cz/v1/geocode?query={place_name}&lang=cs&limit=5&type=regional&type=poi&apikey={API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        locations = json.loads(response.content)
        new_locations = list()
        try:
            for item in locations["items"]:
                if item["label"] in permissible_types:
                    new_locations.append(item)
                else:
                    pass
        except:
            return None
        
        if new_locations:
            return new_locations
        else:
            return None
        return None

def main():
    input_file = 'places.csv'  # Replace with your input file name
    output_file = 'coordinates.txt'  # Replace with your output file name
    data, malfunctional_data = dict(), dict()


    places = process_csv(input_file)

    with open(output_file, 'w') as f:
        progress_bar = tqdm(total=len(places), desc="Processing places.csv")
        for place in places:
            progress_bar.update()
            permissible_type = place["description"]
            place = place["place_name"]
            locations = mapycz_get(place, permissible_type)
            method = "mapy.cz"

            def append(locations, data):
                for idx, location in enumerate(locations):
                    if not place in data:
                        data[place] = {}
                        data[place]["latitude"] =  {}
                        data[place]["longitude"] =  {}
                        data[place]["type"] =  {}
                        if method == "mapy.cz":
                            data[place]["latitude"] = location["position"]["lat"]
                            data[place]["longitude"] = location["position"]["lon"]
                            data[place]["type"] = location["label"]
                        if method == "osm":
                            data[place]["latitude"] = location.latitude
                            data[place]["longitude"] = location.longitude
                            data[place]["type"] = location.raw["type"]
                return data

            if locations is not None:
                data = append(locations, data)
            
            locations = openstreetmap_get(place, permissible_type)
            method = "osm"
            if locations is not None:
                data = append(locations, data)
            else:
                malfunctional_data[place] = {}
                malfunctional_data[place] = "Place not found"
                f.write(f"Coordinates for {place} not found\n")
    progress_bar.close()
    with open("coordinates.json", "w", encoding="utf8") as json_file:
        json.dump(data, json_file, indent=4, ensure_ascii=False)
    with open("malfunctions.json", "w", encoding="utf8") as json_file:
        json.dump(malfunctional_data, json_file, indent=4, ensure_ascii=False)

def new_main():
    input_file = 'places.csv'  # Replace with your input file name
    output_file = 'coordinates.txt'  # Replace with your output file name
    data, malfunctional_data = dict(), dict()


    places = process_csv(input_file)
    with SeleniumMethods() as selenium:
        progress_bar = tqdm(total=len(places), desc="Processing the CSV using SeleniumMethods")
        for place in places:
            place_name = place["place_name"]
            try:
                coordinates = selenium.mapy(place_name)
                data[place_name] = {}
                data[place_name]["latitude"] =  {}
                data[place_name]["longitude"] =  {}
                data[place_name]["type"] =  {}
                data[place_name]["latitude"] = coordinates[0]
                data[place_name]["longitude"] = coordinates[1]
                data[place_name]["type"] = place["description"]
            except:
                malfunctional_data[place_name] = {}
                malfunctional_data[place_name] = "Place not found"
            progress_bar.update(1)
    
    progress_bar.close()
    with open("coordinates.json", "w", encoding="utf8") as json_file:
        json.dump(data, json_file, indent=4, ensure_ascii=False)
    with open("malfunctions.json", "w", encoding="utf8") as json_file:
        json.dump(malfunctional_data, json_file, indent=4, ensure_ascii=False)

# Initialise logger for any use
global logger 
logger = Logger()
if __name__ == "__main__":
    new_main()



