# Local Voila Notebook Outline

Use this outline only when the user explicitly wants a notebook or Voila entrypoint.

## Recommended Cell Order

1. Markdown title and short description
2. imports
3. AppState import or definition
4. construction of the main app component
5. display of the main widget or layout

## Practical Rules

- Keep notebook logic thin. Put real computation in `component/scripts/`.
- Keep state in `component/model/state_manager.py`.
- Avoid burying business logic directly in notebook cells.
- If the app can run cleanly from `app.py`, prefer that and make the notebook a thin wrapper.
