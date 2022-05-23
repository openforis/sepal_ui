from ipyleaflet import TileLayer


class EELayer(TileLayer):
    """
    Wrapper of the TileLayer class to add the ee object as a member.
    useful to get back the values for specific points in a v_inspector

    Args:
        ee_object (ee.object): the ee.object displayed on the map
    """

    ee_object = None
    "ee.object: the ee.object displayed on the map"

    def __init__(self, ee_object, **kwargs):

        self.ee_object = ee_object

        super().__init__(**kwargs)
