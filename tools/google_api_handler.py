import requests

class GoogleAPIHandler:
    def __init__(self, key):
        """Google map API Handler
        Args:
            key(str): google developer key for the API
        """
        self.key = key
    
    def get_geo_info(self, latitude, longitude):
        """Get country name based on the coordinates of the tweets uisng Google Map API
        See https://developers.google.com/maps/documentation/geocoding/start#reverse
        Args:
            latitude(str)
            longitude(str)
        """

        country = None
        resp = None

        # Get latitude/longitude
        latlng = latitude + ',' + longitude
        
        # Request Google API
        link = ("https://maps.googleapis.com/maps/api/geocode/json?latlng=" +
                latlng + "&key=" + self.key)
        resp = requests.get(link)

        if resp:
            for result in resp.json()['results']:
                for item in result["address_components"]:
                    if 'country' in item['types']:
                        country = item["long_name"]
                        break
                    if country is not None:
                        break
        
        return country