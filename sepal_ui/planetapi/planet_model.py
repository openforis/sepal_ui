import httpx
import planet.data_filter as filters
from planet.auth import Auth
from planet.http import AuthSession
from planet.models import Request
from traitlets import Bool

from sepal_ui.message import ms
from sepal_ui.model import Model


class PlanetModel(Model):
    """
    Planet model helper to connect planet API client and perform requests. It can be
    instantiated whether itself or linked with a PlanetView input helper. All the methods
    are aimed to be used without the need of a view.

    Args:
        credentials ([tuple, str], optional): planet API key or tuple of username and password of planet explorer.

    """

    SUBS_URL = "https://api.planet.com/auth/v1/experimental/public/my/subscriptions"
    "str: the url of the planet API subscription"

    active = Bool(False).tag(sync=True)
    "bool: whether if the client has an active subscription or not"

    session = None
    "planet.http.session: planet session."

    def __init__(self, credentials=None):

        if credentials:
            self.init_session(credentials)

    def init_session(self, credentials):
        """Initialize planet client with api key or credentials. It will handle errors.

        Args:
            credentials (list): planet API key of username and password pair of planet explorer.
        """

        if not all(credentials):
            raise ValueError(ms.planet.exception.empty)

        if len(credentials) == 2:
            auth = Auth.from_login(*credentials)
        else:
            auth = Auth.from_key(credentials[0])

        self.session = AuthSession()
        self.session._client = httpx.Client(auth=auth)
        self._is_active()

        return

    def _is_active(self):
        """check if the key has an associated active subscription"""

        # get the subs from the api key
        subs = self.get_subscriptions()

        # read the subs
        # it will be empty if no sub are set
        self.active = any([True for sub in subs if sub.get("state") == "active"])

        return

    def get_subscriptions(self):
        """load the user subscriptions and throw an error if none are found"""

        req = Request(self.SUBS_URL, method="GET")
        response = self.session.request(req)

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
            [
                filters.geometry_filter(aoi),
                filters.range_filter("cloud_cover", lte=cloud_cover),
                filters.date_range_filter("acquired", gt=start),
                filters.date_range_filter("acquired", lt=end),
            ]
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
