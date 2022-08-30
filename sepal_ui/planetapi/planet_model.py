import asyncio
from datetime import datetime
from itertools import compress

import nest_asyncio
import planet.data_filter as filters
from planet import DataClient
from planet.auth import Auth
from planet.exceptions import NoPermission
from planet.http import Session
from planet.models import Request
from traitlets import Bool, Dict

from sepal_ui.message import ms
from sepal_ui.model import Model

# known problem https://github.com/jupyter/notebook/issues/3397
nest_asyncio.apply()


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

    credentials = None
    "list: list containing [api_key] or pair of [username, password] to log in"

    session = None
    "planet.http.session: planet session."

    subscriptions = Dict().tag(sync=True)
    "list[(dict)]: list containing all the dictionary info from the available subscriptions"

    active = Bool(False).tag(sync=True)
    "Bool: value to determine if at least one subscription has the active true state"

    def __init__(self, credentials=None):

        self.subscriptions = {}
        self.session = None
        self.active = False

        if credentials:
            self.init_session(credentials)

    def init_session(self, credentials):
        """Initialize planet client with api key or credentials. It will handle errors.

        Args:
            credentials (list): planet API key of username and password pair of planet explorer.
        """

        if not isinstance(credentials, list):
            credentials = [credentials]

        if not all(credentials):
            raise ValueError(ms.planet.exception.empty)

        if len(credentials) == 2:
            self.auth = Auth.from_login(*credentials)
        else:
            self.auth = Auth.from_key(credentials[0])

        self.session = Session(auth=self.auth)
        self._is_active()

        return

    def _is_active(self):
        """check if the key has an associated active subscription"""

        self.subscriptions = {}

        # get the subs from the api key and save them in the model. It will be useful
        # to avoid doing more calls.
        subs = self.get_subscriptions()

        # As there is not any key that identify the nicfi contract,
        # let's find though all the subscriptions a representative name
        wildcards = [
            "Level_0",
            "Level_1",
            "Level2",
        ]

        masks = [[wildc in str(sub) for wildc in wildcards] for sub in subs]
        others = [i for i, mask in enumerate(masks) if not any(mask)]

        subs_groups = [
            list(enumerate(others)),
            enumerate(["level_0", "level_1", "level_2"]),
        ]

        def get_subscription(nicfi, index):

            if nicfi:
                mask = masks[index]
                return next(iter(list(compress(subs, mask))))
            else:
                return subs[subs_groups[nicfi][index][1]]

        self.subscriptions = {
            group: {
                sub_name: get_subscription(bool(nicfi), i)
                for i, sub_name in subs_groups[bool(nicfi)]
            }
            for nicfi, group in enumerate(["others", "nicfi"])
        }

        # self.active = any()
        states = self.search_status(self.subscriptions)
        self.active = any([next(iter(d.values())) for d in states])

        return

    def get_subscriptions(self):
        """load the user subscriptions and return empty list if nothing found"""

        req = Request(self.SUBS_URL, method="GET")

        try:
            response = asyncio.run(self.session.request(req))
            if response.status_code == 200:
                return response.json()

        except NoPermission:
            self.subscriptions = {}
            raise Exception(
                "You don't have permission to access to this resource. Check your input data."
            )

        except Exception as e:
            self.subscriptions = {}
            raise e

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

        start, end = [
            date.strftime("%Y-%m-%d")
            for date in [start, end]
            if isinstance(date, datetime)
        ] or [start, end]

        and_filter = filters.and_filter(
            [
                filters.geometry_filter(aoi),
                filters.range_filter("cloud_cover", lte=cloud_cover),
                filters.date_range_filter(
                    "acquired", gt=datetime.strptime(start, "%Y-%m-%d")
                ),
                filters.date_range_filter(
                    "acquired", lt=datetime.strptime(end, "%Y-%m-%d")
                ),
            ]
        )

        # PSScene3Band and PSScene4Band item type and assets will be deprecated by January 2023
        # But we'll keep them here because there are images tagged with these labels
        # item types from https://developers.planet.com/docs/apis/data/items-assets/

        item_types = ["PSScene", "PSScene3Band", "PSScene4Band"]

        async def main():
            """Create an asyncrhonous function here to avoid making the main get_items
            as async. So we can keep calling get_items without any change."""
            client = DataClient(self.session)
            items = await client.search(item_types, and_filter, name="quick_search")
            items.limit = limit_to_x_pages
            items_list = [item async for item in items]
            return items_list

        return asyncio.run(main())

    @staticmethod
    def search_status(d):

        states = []

        def recursive(d, k):
            if "plan" in d:
                plan = d.get("plan")
                state = True if plan.get("state") == "active" else False
                states.append({k: state})

            for k, v in d.items():
                if isinstance(v, dict):
                    item = recursive(v, k)
                    if item:
                        return item

        recursive(d, None)

        return states
