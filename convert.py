# This should be some simple code to get the POIs off OpenStreetMap
# Traces: ChatGPT

from geopy.geocoders import Nominatim
import json
import csv
from tqdm import tqdm

def process_csv(file_path):
    places_data = []

    def interpret_description(czech_description):
        mapping = {
            'řeka': ['river', 'waterway'],
            'jezero': ['lake', 'water'],
            'přehrada': ['reservoir', 'water', 'dam'],
            'rybník': ['reservoir', 'water', 'lake'],
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

def get_location_details(place_name, permissible_types=["river"]):
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

def main():
    input_file = 'places.csv'  # Replace with your input file name
    output_file = 'coordinates.txt'  # Replace with your output file name
    data = dict()


    places = process_csv(input_file)

    with open(output_file, 'w') as f:
        progress_bar = tqdm(total=len(places), desc="Processing places.csv")
        for place in places:
            progress_bar.update()
            permissible_type = place["description"]
            place = place["place_name"]
            locations = get_location_details(place, permissible_type)

            if locations is not None:
                for idx, location in enumerate(locations):
                    if not place in data:
                        data[place] = {}
                        data[place]["latitude"] =  {}
                        data[place]["longitude"] =  location.longitude
                        data[place]["latitude"] =  location.latitude
                        data[place]["type"] =  {}
                        data[place]["type"] =  location.raw["type"]
                    # Extract additional information
                    building_type = location.raw.get('type', 'N/A')
                    f.write(f"{place} Match {idx + 1}: {location.latitude}, {location.longitude}\n")
                    f.write(f"  Building Type: {building_type}\n")
                    # You can access more details from the 'location.raw' dictionary
            else:
                f.write(f"Coordinates for {place} not found\n")
    progress_bar.close()
    with open("coordinates.json", "w", encoding="utf8") as json_file:
        json.dump(data, json_file, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    main()



