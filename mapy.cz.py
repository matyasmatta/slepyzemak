import requests
import json

API_KEY = "YOUR_API_KEY"

def mapycz_get(place_name):
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
        data = json.loads(response.content)

            return data["text"]
    return None

print(get_coordinates_from_mapycz("Praha"))