import asyncio
from datetime import datetime
from typing import Dict, List, Union

import nest_asyncio
import planet.data_filter as filters
import traitlets as t
from planet import DataClient
from planet.auth import Auth
from planet.exceptions import NoPermission
from planet.http import Session

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
        credentials: planet API key or tuple of username and password of planet explorer.

    """

    SUBS_URL: str = (
        "https://api.planet.com/auth/v1/experimental/public/my/subscriptions"
    )
    "The url of the planet API subscription"

    credentials: List[str] = []
    "list containing [api_key] or pair of [username, password] to log in"

    session: Session
    "planet.http.session: planet session."

    subscriptions: t.Dict = t.Dict({}).tag(sync=True)
    "All the dictionary info from the available subscriptions"

    active = t.Bool(False).tag(sync=True)
    "Value to determine if at least one subscription has the active true state"

    def __init__(self, credentials: Union[str, List[str]] = "") -> None:

        self.subscriptions = {}
        self.session = None
        self.active = False

        if credentials:
            self.init_session(credentials)

    def init_session(self, credentials: Union[str, List[str]]) -> None:
        """Initialize planet client with api key or credentials. It will handle errors.

        Args:
            credentials: planet API key or username and password pair of planet explorer.
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

    def _is_active(self) -> None:
        """
        check if the key has an associated active subscription and change the state button accordingly
        """

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

        subscriptions = {"nicfi": [], "others": []}

        for sub in subs:
            for w in wildcards:
                if w in str(sub):
                    subscriptions["nicfi"].append(sub)
                    break
            if sub not in subscriptions["nicfi"]:
                subscriptions["others"].append(sub)

        self.subscriptions = subscriptions

        states = self.search_status(self.subscriptions)
        self.active = any([next(iter(d.values())) for d in states])

        return

    def get_subscriptions(self) -> dict:
        """
        load the user subscriptions

        Returns:
            the dictionnary of user subscription or empty list if nothing found
        """

        req = self.session.request("GET", self.SUBS_URL)

        try:
            response = asyncio.run(req)
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

    def get_items(
        self,
        aoi: dict,
        start: str,
        end: str,
        cloud_cover: float,
        limit_to_x_pages: int = -1,
    ) -> list:
        """
        Request imagery items from the planet API for the requested dates.

        Args:
            aoi: geojson clipping geometry
            start: the start of the request (YYYY-mm-dd))
            end: the end of the request (YYYY-mm-dd))
            cloud_cover: maximum cloud coverage.
            limit_to_x_pages: number of pages to constrain the search. Defaults to -1 to use all of them.

        Returns:
            items found using the search query

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
    def search_status(d: dict) -> List[Dict[str, bool]]:

        states = []

        for v in d.values():
            for subs in v:
                if "plan" in subs:
                    plan = subs.get("plan")
                    state = True if plan.get("state") == "active" else False
                    states.append({plan.get("name"): state})

        return states
