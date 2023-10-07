# This should be some simple code to get the POIs off OpenStreetMap
# Traces: ChatGPT

from geopy.geocoders import Nominatim
import json
import csv
from tqdm import tqdm
import requests

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
        return mapping.get(czech_description, [])

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


if __name__ == "__main__":
    main()



