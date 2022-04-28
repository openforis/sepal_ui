import sepal_ui.scripts.utils as su
from traitlets import observe, dlink, Bool
from planet_model import PlanetModel
import ipyvuetify as v
import sepal_ui.sepalwidgets as sw


class StateIcon(sw.Tooltip):

    valid = Bool(False).tag(sync=True)

    def __init__(self, model):

        self.right = True
        self.icon = v.Icon(children=["fas fa-circle"], color="red", small=True)

        super().__init__(self.icon, "Not connected")

        dlink((model, "active"), (self, "valid"))

    @observe("valid")
    def swap(self, change):
        """Swap between active and deactive mode"""

        if change["new"]:
            self.icon.color = "green"
            self.children = ["Connected"]
        else:
            self.icon.color = "red"
            self.children = ["Not connected"]


class PlanetView(sw.Layout):
    def __init__(self, *args, btn=None, alert=None, planet_model=None, **kwargs):

        self.class_ = "d-flex flex-wrap align-center"
        super().__init__(*args, **kwargs)

        self.planet_model = planet_model if planet_model else PlanetModel()
        self.btn = btn if btn else sw.Btn("Validate", small=True, class_="mr-1")
        self.alert = alert if alert else sw.Alert()

        self.w_username = sw.TextField(
            label="Planet username", class_="mr-2", v_model=""
        )
        self.w_password = sw.PasswordField(label="Planet password")
        self.w_key = sw.PasswordField(label="Planet API key", v_model="").hide()
        self.w_state = StateIcon(self.planet_model)

        self.w_method = v.Select(
            label="Login method",
            class_="mr-2",
            v_model="credentials",
            items=[
                {"value": "api_key", "text": "API Key"},
                {"value": "credentials", "text": "Credentials"},
            ],
        )

        w_validation = v.Flex(
            style_="flex-grow: 0 !important;",
            children=[self.btn, self.w_state],
            class_="pr-1",
        )

        self.children = [
            v.Flex(children=[self.w_method], sm12=True, md3=True),
            self.w_username,
            self.w_password,
            self.w_key,
        ]

        if not btn:
            self.set_children(w_validation, "last")

        self.w_method.observe(self._swap_inputs, "v_model")
        self.btn.on_event("click", self.validate)

    def _swap_inputs(self, change):
        """Swap between credentials and api key inputs"""

        if change["new"] == "api_key":
            self.w_username.hide()
            self.w_password.hide()
            self.w_key.show()
        else:
            self.w_username.show()
            self.w_password.show()
            self.w_key.hide()

    @su.loading_button()
    def validate(self, *args):
        """Initialize planet client and validate if is active"""

        if self.w_method.v_model == "credentials":
            credentials = (self.w_username.v_model, self.w_password.v_model)
        else:
            credentials = self.w_key.v_model

        self.planet_model._init_client(credentials)
