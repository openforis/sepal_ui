"""Administrative components for session and model management in Solara applications."""

import logging
from typing import Any, Optional, Union

import reacton.ipyvuetify as v
import solara

from sepal_ui.solara.session_manager import SessionManager

logger = logging.getLogger("sepalui.admin")


def get_current_session_info() -> dict:
    """Get information about the current session."""
    session_manager = SessionManager()
    kernel_id = session_manager.get_kernel_id()

    # Get the current session directly
    sessions = session_manager.list_sessions()
    current_session = sessions.get(kernel_id)

    if current_session is None:
        return {
            "kernel_id": kernel_id,
            "username": None,
            "has_gee_interface": False,
            "has_sepal_client": False,
            "session_ready": False,
        }

    gee_interface = current_session.get("gee_interface")
    sepal_client = current_session.get("sepal_client")
    username = current_session.get("username", "unknown")

    return {
        "kernel_id": kernel_id,
        "username": username,
        "has_gee_interface": gee_interface is not None,
        "has_sepal_client": sepal_client is not None,
        "session_ready": gee_interface is not None,
    }


def get_sessions_overview() -> dict:
    """Get an overview of all sessions."""
    session_manager = SessionManager()
    sessions = session_manager.list_sessions()

    session_details = []
    ready_sessions = 0

    for kernel_id, session in sessions.items():
        gee_interface = session.get("gee_interface")
        sepal_client = session.get("sepal_client")
        username = session.get("username", "unknown")

        session_ready = gee_interface is not None
        if session_ready:
            ready_sessions += 1

        session_details.append(
            {
                "kernel_id": kernel_id,
                "username": username,
                "has_gee_interface": gee_interface is not None,
                "has_sepal_client": sepal_client is not None,
                "session_ready": session_ready,
            }
        )

    return {
        "total_sessions": len(sessions),
        "ready_sessions": ready_sessions,
        "sessions": session_details,
    }


@solara.component
def AdminButton(
    models: Optional[Union[Any, list[Any]]] = None, logger_instance: Optional[logging.Logger] = None
):
    """A button component that's only visible to admin users and opens a session dialog.

    Args:
        models: Single traitlets model or list of traitlets models to display in the dialog
        logger_instance: Optional logger instance to use for debug logging

    Usage:
        from admin_session_dialog import AdminButton

        # Single model (backwards compatible):
        AdminButton(models=my_model, logger_instance=my_logger)

        # Multiple models:
        AdminButton(models=[my_model1, my_model2], logger_instance=my_logger)

        # No models:
        AdminButton(logger_instance=my_logger)

        # Old style still works:
        AdminButton(models=my_model)
    """
    dialog_open, set_dialog_open = solara.use_state(False)

    session_info, set_session_info = solara.use_state({})
    sessions_overview, set_sessions_overview = solara.use_state({})

    models_data, set_models_data = solara.use_state([])
    active_tab, set_active_tab = solara.use_state(0)

    username = get_current_session_info()["username"]

    def is_admin_user() -> bool:
        """Check if the current user has admin privileges.

        This checks if the username is 'admin'.
        """
        return username and username.lower() in ["admin", "dguerrero"]

    def normalize_models() -> list[Any]:
        """Normalize the models input to always return a list."""
        if models is None:
            return []
        elif isinstance(models, list):
            return models
        else:
            # Single model case - wrap in a list
            return [models]

    # Handler to update model data
    def update_models_data():
        normalized_models = normalize_models()

        if len(normalized_models) > 0:
            try:
                import pprint

                models_data_list = []
                for i, model in enumerate(normalized_models):
                    try:
                        # Use the model's export_data method to get structured data
                        model_data_dict = model.export_data()
                        formatted_str = pprint.pformat(model_data_dict, width=80, depth=3)
                        models_data_list.append(
                            {"index": i, "type": type(model).__name__, "data": formatted_str}
                        )
                    except Exception as e:
                        try:
                            model_str = repr(model)
                            models_data_list.append(
                                {"index": i, "type": type(model).__name__, "data": model_str}
                            )
                        except Exception:
                            models_data_list.append(
                                {
                                    "index": i,
                                    "type": type(model).__name__,
                                    "data": f"Error getting model data: {str(e)}",
                                }
                            )

                set_models_data(models_data_list)

            except Exception as e:
                set_models_data(
                    [{"index": 0, "type": "Error", "data": f"Error processing models: {str(e)}"}]
                )
        else:
            set_models_data([])

    def open_dialog():
        current_info = get_current_session_info()
        overview = get_sessions_overview()

        set_session_info(current_info)
        set_sessions_overview(overview)

        update_models_data()

        set_dialog_open(True)

    def close_dialog():
        set_dialog_open(False)

    def debug_log_models():
        active_logger = logger_instance if logger_instance is not None else logger
        normalized_models = normalize_models()

        if len(normalized_models) > 0:
            for i, model in enumerate(normalized_models):
                active_logger.debug(f"Model {i}: {model}")
        else:
            active_logger.debug("No models provided")

    # Only render the button if user is admin
    if not is_admin_user():
        return

    # Create the debug button (only if models are provided)
    normalized_models_for_button = normalize_models()
    if len(normalized_models_for_button) > 0:
        button_label = (
            "Debug: Log Model" if len(normalized_models_for_button) == 1 else "Debug: Log Models"
        )
        solara.Button(
            label=button_label,
            on_click=debug_log_models,
            color="info",
            icon_name="mdi-bug",
            outlined=True,
        )

    # Create the admin button
    solara.Button(
        label="Admin panel",
        on_click=open_dialog,
        color="primary",
        small=True,
        icon_name="mdi-shield-account",
    )

    with v.Dialog(
        v_model=dialog_open, on_v_model=set_dialog_open, max_width="900px", scrollable=True
    ):
        with solara.v.Card():
            solara.v.CardTitle(children=["Admin: Session & Models Information"])

            with solara.v.CardText():
                with v.Tabs(v_model=active_tab, on_v_model=set_active_tab):
                    # Dynamic tab label based on number of models
                    model_count = len(normalize_models())
                    if model_count == 1:
                        v.Tab(children=["Model Data"])
                    else:
                        v.Tab(children=["Models Data"])
                    v.Tab(children=["Session Info"])

                with v.TabsItems(v_model=active_tab, on_v_model=set_active_tab):
                    with v.TabItem():
                        _render_model_content(normalize_models(), models_data, update_models_data)

                    with v.TabItem():
                        _render_session_content(
                            username, is_admin_user(), session_info, sessions_overview
                        )

            with solara.v.CardActions():
                solara.v.Spacer()
                solara.Button(
                    label="Get Data",
                    on_click=open_dialog,
                    text=True,
                    color="primary",
                )
                solara.Button(label="Close", on_click=close_dialog, color="primary")


def _render_model_content(
    normalized_models: list[Any], models_data: list, update_models_data: callable
):
    """Render the model information content."""
    solara.Markdown("## Models Data")

    if len(normalized_models) > 0:
        # Add update button at the top
        with solara.Row():
            if len(normalized_models) == 1:
                solara.Text(f"Model Type: {type(normalized_models[0]).__name__}")
            else:
                solara.Text(f"Total Models: {len(normalized_models)}")
            solara.v.Spacer()
            solara.Button(
                label="Update Models Data",
                on_click=update_models_data,
                color="primary",
                icon_name="mdi-refresh",
                outlined=True,
            )

        solara.Markdown("### Models Representation:")

        # Display each model's data
        for model_info in models_data:
            model_index = model_info.get("index", 0)
            model_type = model_info.get("type", "Unknown")
            model_data = model_info.get("data", "No data available")

            # Only show index if there are multiple models
            if len(normalized_models) > 1:
                solara.Markdown(f"#### Model {model_index + 1} ({model_type})")
            else:
                solara.Markdown(f"#### {model_type}")

            with solara.v.Card(outlined=True):
                with solara.v.CardText():
                    solara.Preformatted(
                        model_data,
                        style="background-color: #f5f5f5; padding: 16px; font-family: monospace;",
                    )
    else:
        solara.Text("No models provided")
        solara.Text(
            "Pass a traitlets model or list of models to the AdminButton component to see their data here."
        )


def _render_session_content(
    username: str, is_admin: bool, session_info: dict, sessions_overview: dict
):
    """Render the session information content."""
    solara.Markdown("## Current User Information")
    solara.FileBrowser()
    solara.Text(f"Current User: {username}")
    solara.Text(f"Admin Access: {'✅ Yes' if is_admin else '❌ No'}")

    solara.Markdown("---")

    solara.Markdown("## Current Session Information")

    if session_info:
        with solara.Column(gap="0.5rem"):
            solara.Text(f"Kernel ID: {session_info.get('kernel_id', 'N/A')}")
            solara.Text(f"Username: {session_info.get('username', 'N/A')}")
            solara.Text(f"Session Ready: {'✅' if session_info.get('session_ready') else '❌'}")
            solara.Text(
                f"GEE Interface: {'✅ Available' if session_info.get('has_gee_interface') else '❌ Not Available'}"
            )
            solara.Text(
                f"Sepal Client: {'✅ Available' if session_info.get('has_sepal_client') else '❌ Not Available'}"
            )
    else:
        solara.Text("No session information available.")

    solara.Markdown("---")

    solara.Markdown("## Sessions Overview")

    if sessions_overview:
        solara.Text(f"Total Active Sessions: {sessions_overview.get('total_sessions', 0)}")
        solara.Text(f"Ready Sessions: {sessions_overview.get('ready_sessions', 0)}")

        session_details = sessions_overview.get("sessions", [])
        if session_details:
            solara.Markdown("### Session Details:")

            for i, session in enumerate(session_details, 1):
                with solara.Card(f"Session {i}"):
                    with solara.Column(gap="0.25rem"):
                        solara.Text(f"Kernel ID: {session.get('kernel_id', 'N/A')}")
                        solara.Text(f"Username: {session.get('username', 'N/A')}")
                        solara.Text(
                            f"GEE Interface: {'✅' if session.get('has_gee_interface') else '❌'}"
                        )
                        solara.Text(
                            f"Sepal Client: {'✅' if session.get('has_sepal_client') else '❌'}"
                        )
                        solara.Text(
                            f"Session Ready: {'✅' if session.get('session_ready') else '❌'}"
                        )
        else:
            solara.Text("No active sessions found.")
    else:
        solara.Text("Sessions overview not available.")
