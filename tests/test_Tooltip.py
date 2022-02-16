from sepal_ui import sepalwidgets as sw


class TestTooltip:
    def test_init(self):

        # Arrange
        btn = sw.Btn("click")
        tooltip = sw.Tooltip(widget=btn, tooltip="tooltip")

        # Check tooltip is having the tooltip message

        assert tooltip.children == ["tooltip"]

        # Let's be sure that we can change the tooltip initial message

        tooltip.children = ["This is a new message"]

        assert tooltip.children == ["This is a new message"]

        return
