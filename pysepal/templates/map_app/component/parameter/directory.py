"""All directories used in the application."""

from pathlib import Path

# this directory is the root directory of all sepal dashboard app.
# Change it if you develop in another environment.
module_dir = Path.home() / "module_results"
module_dir.mkdir(exist_ok=True)
