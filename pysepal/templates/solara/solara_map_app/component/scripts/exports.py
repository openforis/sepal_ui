"""Declare the datasets the export dialog is allowed to offer."""

from pysepal.solara.components.export import ExportSource, ResolvedExport


def export_sources(aoi_value, outputs) -> list[ExportSource]:
    """Declare what the export dialog is allowed to offer.

    The dialog only lists datasets a page explicitly registers here.
    """
    sources: list[ExportSource] = []

    if aoi_value is not None and aoi_value.feature_collection is not None:
        sources.append(
            ExportSource(
                id="selected_aoi",
                label="Selected AOI boundary",
                kind="table",
                description="The AOI feature collection currently selected in the sidebar.",
                resolve=lambda fc=aoi_value.feature_collection, name=aoi_value.name: ResolvedExport(
                    ee_object=fc,
                    default_name=name,
                    drive_folder="pysepal_exports",
                    sepal_folder="exports",
                ),
            )
        )

    if outputs is None:
        return sources

    def image_source(source_id, label, image, description, bands=None, default_bands=None):
        return ExportSource(
            id=source_id,
            label=label,
            kind="image",
            description=description,
            resolve=lambda: ResolvedExport(
                ee_object=image,
                default_name=f"{outputs.name_prefix}_{source_id}",
                region=outputs.region,
                default_scale=300,
                bands=bands,
                default_bands=default_bands,
                drive_folder="pysepal_exports",
                sepal_folder="exports",
            ),
        )

    sources += [
        image_source(
            "pixel_area",
            "Pixel area (m²)",
            outputs.pixel_area,
            "Continuous output. Its map legend is the gradient built from vis_params.",
        ),
        image_source(
            "elevation_class",
            "Elevation classes",
            outputs.elevation_class,
            "Classified output. Its legend lists per-class areas in the detail column.",
        ),
        image_source(
            "multi_band",
            "Multi-band demo (3 bands)",
            outputs.multi_band,
            "Shows the ExportLauncher band picker: keep every band or narrow to a subset.",
            bands=("pixel_area_m2", "elevation_class", "flag"),
            # Pre-select the useful bands; `flag` stays deselectable from the dialog.
            default_bands=("pixel_area_m2", "elevation_class"),
        ),
    ]

    return sources
