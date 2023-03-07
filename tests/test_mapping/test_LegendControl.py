import re

from sepal_ui.mapping import LegendControl


def test_init() -> None:
    """Init the control object"""
    legend_dict = {
        "forest": "#b3842e",
        "non forest": "#a1458e",
        "secondary": "#324a88",
        "success": "#3f802a",
        "info": "#79b1c9",
        "warning": "#b8721d",
    }

    # hardcode expected
    expected_labels = [
        "Forest",
        "Non forest",
        "Secondary",
        "Success",
        "Info",
        "Warning",
    ]

    legend = LegendControl(legend_dict, title="Legend")

    # Check all the default values
    assert legend.title == "Legend"
    assert legend._html_title.children[0] == "Legend"
    assert legend.legend_dict == legend_dict

    # check all the labels and colors are present in the html
    assert all([label in str(legend._html_table) for label in expected_labels])
    assert all([color in str(legend._html_table) for color in legend_dict.values()])

    # Check the lenght
    assert len(legend) == 6

    return


def test_set_legend() -> None:
    """Set a legend with values (FNF)"""
    legend_dict = {
        "forest": "#b3842e",
        "info": "#79b1c9",
    }

    legend = LegendControl(legend_dict)

    new_legend = {
        "forest": "#b3842e",
        "non forest": "#3f802a",
    }

    # trigger the event
    legend.legend_dict = new_legend

    assert legend.legend_dict == new_legend

    # Check that previous labels are not in the new legend
    assert "Info" not in str(legend._html_table)

    # check all the new labels are present in the legend
    assert all([label in str(legend._html_table) for label in ["Forest", "Non forest"]])

    # Act: change the view

    # Check current view
    assert legend.vertical is True

    # in the vertical view, there should be at least two rows
    assert str(legend._html_table).count("'tr'") == 2

    legend.vertical = False
    assert str(legend._html_table).count("'tr'") == 0

    return


def test_update_title() -> None:
    """Update the title of an existing legend control"""
    legend_dict = {
        "forest": "#b3842e",
        "info": "#79b1c9",
    }

    legend = LegendControl(legend_dict)

    legend.title = "leyenda"

    # Check all the default values
    assert legend.title == "leyenda"
    assert legend._html_title.children[0] == "leyenda"

    return


def test_color_box() -> None:
    """Use color boxes when multiple values (forest, info)"""
    legend_dict = {
        "forest": "#b3842e",
        "info": "#79b1c9",
    }
    legend = LegendControl(legend_dict)
    str_box = re.sub("[ ]+", "", str(legend.color_box("blue", 50)[0]))

    assert "fill:#0000ff" in str_box
    assert "width='50'" in str_box
    assert "'height='25.0'" in str_box

    return
