from planet import api
from planet.api import filters


class PlanetModel:

    SUBS_URL = "https://api.planet.com/auth/v1/experimental/public/my/subscriptions"

    def __init__(self, api_key=None):

        """Planet helper class useful to handle recurrent sepal module operations


        Args:
            api_key (str): plain text planet api key with valid subscription

        Params:
            client (planet.api.ClientV1): planet api initialized client.
            active (bool): whether if the client has an active subscription or not
        """

        self.client = None
        self.active = False

        self._init_client(api_key)

    def _init_client(self, api_key):
        """return the client api object"""

        self.client = api.ClientV1(api_key=api_key)
        self._is_active()

    def _is_active(self):
        """check if the key has an associated active subscription"""

        # get the subs from the api key
        subs = self.get_subscriptions()

        # read the subs
        # it will be empty if no sub are set
        self.active = any([True for sub in subs if sub.get("state") == "active"])

    def get_subscriptions(self):
        """load the user subscriptions and throw an error if none are found"""

        response = self.client.dispatcher.dispatch_request(
            "get", self.SUBS_URL, auth=self.client.auth
        )

        if response.status_code == 200:
            return response.json()

        return []

    def get_items(self, aoi, start, end, cloud_cover, limit_to_x_pages=None):
        """
        Request imagery items from the planet API for the requested dates.

        Args:
            aoi(geojson, polygon): clipping geometry
            start(str, YYYY-mm-dd): the start of the request
            end (str, YYYY-mm-dd): the end of the request
            cloud_cover (float): maximum cloud coverage.
            limit_to_x_pages (int): number of pages to constrain the search.
                Defaults None to use all of them.

        Return:
            items (list): items found using the search query

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
        limit_to_x_pages = None
        for page in result.iter(limit_to_x_pages):
            items_pages.append(page.get())

        items = [item for page in items_pages for item in page["features"]]

        return items
