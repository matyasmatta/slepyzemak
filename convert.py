# This should be some simple code to get the POIs off OpenStreetMap
# Traces: ChatGPT

from geopy.geocoders import Nominatim
import json

def to_json(data):
    pass

def get_location_details(place_name):
    geolocator = Nominatim(user_agent="convert.py")
    locations = geolocator.geocode(place_name, exactly_one=False, country_codes="cz")
    
    if locations:
        return locations
    else:
        return None

def main():
    input_file = 'places.txt'  # Replace with your input file name
    output_file = 'coordinates.txt'  # Replace with your output file name
    data = dict()


    with open(input_file, 'r') as f:
        places = f.readlines()

    with open(output_file, 'w') as f:
        for place in places:
            place = place.strip()
            locations = get_location_details(place)

            if locations is not None:
                for idx, location in enumerate(locations):
                    if idx == 0:
                        data[place] = {}
                        data[place]["latitude"] =  {}
                        data[place]["longitude"] =  location.longitude
                        data[place]["latitude"] =  location.latitude
                    # Extract additional information
                    building_type = location.raw.get('type', 'N/A')
                    f.write(f"{place} Match {idx + 1}: {location.latitude}, {location.longitude}\n")
                    f.write(f"  Building Type: {building_type}\n")
                    # You can access more details from the 'location.raw' dictionary
            else:
                f.write(f"Coordinates for {place} not found\n")
    with open("coordinates.json", "w") as json_file:
        json.dump(data, json_file, indent=4)


if __name__ == "__main__":
    main()



