from planet.api import APIException
from planet.api.client import InvalidIdentity

from sepal_ui.model import Model
from traitlets import Bool
from planet import api
from planet.api import filters


class PlanetModel(Model):

    SUBS_URL = "https://api.planet.com/auth/v1/experimental/public/my/subscriptions"

    active = Bool(False).tag(sync=True)
    "bool: whether if the client has an active subscription or not"

    def __init__(self, credentials=None):

        """Planet helper class useful to handle recurrent sepal module operations

        Args:
            credentials ([tuple, str], optional): tuple of username and password of planet explorer. Or string API key.

        Params:
            client (planet.api.ClientV1): planet api initialized client.

        """

        # Instantiate a fake client to avoid
        # https://github.com/12rambau/sepal_ui/pull/439#issuecomment-1121538658
        # This will be changed when planet launches new release
        self.client = api.ClientV1("fake_init")
        self._init_client(credentials)

    def _init_client(self, credentials, event=None):
        """Initialize planet client with api key or credentials. It will handle errors
        if the method is called from an event (view)

        Args:
            event (bool): whether to initialize from an event or not.
        """

        credentials_ = credentials
        if event and not any(tuple(credentials)):
            raise ValueError("Please fill the required field(s).")

        if isinstance(credentials_, tuple):
            try:
                credentials_ = api.ClientV1().login(*credentials_)["api_key"]

            except InvalidIdentity:
                raise InvalidIdentity("Invalid email or password")

            except APIException:
                # This error will be triggered when email is passed in bad format
                raise APIException("Please check the format of your inputs.")

        self.client.auth.value = credentials_
        self._is_active()

        if event and not self.active:
            raise Exception(
                "Your credentials do not have any valid planet subscription."
            )

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
