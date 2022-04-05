from planet import api
from planet.api import filters
import requests


class PlanetKey:

    SUBS_URL = "https://api.planet.com/auth/v1/experimental/public/my/subscriptions"

    def __init__(self, api_key=None):

        self.api_key = None
        self.client = None

        self.active = False

        if api_key:
            self.init_client(api_key)

    def init_client(self, api_key):
        """return the client api object"""

        self.api_key = api_key
        self.client = api.ClientV1(api_key=self.api_key)
        self.is_active()

    def is_active(self):
        """check if the key is activated"""

        # get the subs from the api key
        subs = self.get_subscription()

        # read the subs
        # it will be empty if no sub are set
        self.active = any([True for s in subs if s["state"] == "active"])

    def get_subscription(self):
        """load the user subscriptions and throw an error if none are found"""

        resp = requests.get(self.SUBS_URL, auth=(self.api_key, ""))
        subscriptions = resp.json()

        if resp.status_code == 200:
            return subscriptions

        return []

    def get_planet_items(self, aoi, start, end, cloud_cover):
        """
        Request imagery items from the planet API for the requested dates.

        Args:
            aoi(geojson): clipping geometry
            start(datetime.date): the start of the request
            end (datetime.date): the end of the request
            cloud_cover (int): cloud coverage threshold

        Return:
            (list): items from the Planet API
        """

        query = filters.and_filter(
            filters.geom_filter(aoi),
            filters.range_filter("cloud_cover", lte=cloud_cover),
            filters.date_range("acquired", gt=start),
            filters.date_range("acquired", lt=end),
        )

        # Skipping REScene because is not orthorrectified and
        # cannot be clipped.
        asset_types = ["PSScene"]

        # build the request
        request = filters.build_search_request(query, asset_types)
        result = self.client.quick_search(request)

        # get all the results
        items_pages = []
        for page in result.iter(None):
            items_pages.append(page.get())

        items = [item for page in items_pages for item in page["features"]]

        return items
