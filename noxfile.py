"""All the process that can be run using nox.

The nox run are build in isolated environment that will be stored in .nox. to force the venv update, remove the .nox/xxx folder.
"""

import tempfile
from pathlib import Path

import nox

# pysepal-api is not yet on PyPI; build a wheel from the local sibling repo when present
# so that pip's resolver can satisfy the pysepal-api>=0.1,<1 constraint via --find-links.
_PYSEPAL_API_LOCAL = Path(__file__).parent.parent / "pysepal-api"


def _preinstall_pysepal_api(session: nox.Session) -> None:
    """Pre-install pysepal-api from the local sibling repo into the session venv.

    pysepal-api ships as a pre-release (0.1.0.dev0) until it hits PyPI.  We
    build a wheel on the fly and install it directly so that pip's subsequent
    ``.[test]`` install sees the dependency already satisfied and does not try
    to resolve it from PyPI.  When pysepal-api is eventually published on PyPI
    this helper becomes a no-op (the local dir will be absent in CI / fresh
    checkouts).
    """
    if not _PYSEPAL_API_LOCAL.is_dir():
        return
    wheel_dir = Path(tempfile.mkdtemp(prefix="pysepal-api-wheel-"))
    session.run(
        "python",
        "-m",
        "pip",
        "wheel",
        "--no-deps",
        "--wheel-dir",
        str(wheel_dir),
        str(_PYSEPAL_API_LOCAL),
        silent=True,
    )
    wheels = list(wheel_dir.glob("pysepal_api-*.whl"))
    if wheels:
        session.install(str(wheels[0]))


nox.options.sessions = ["lint", "test", "docs"]


@nox.session(reuse_venv=True)
def lint(session):
    """Apply the pre-commits."""
    session.install("pre-commit")
    session.run("pre-commit", "run", "--all-files", *session.posargs)


@nox.session(reuse_venv=False)
def test(session):
    """Run all the test using the environment variable of the running machine."""
    _preinstall_pysepal_api(session)
    session.install(".[test]")
    session.run("pip", "list")

    # if we are in the sepal-venv, force earthengine api fork
    if "sepal-user" in session.virtualenv.location:
        session.run(
            "pip",
            "install",
            "git+https://github.com/openforis/earthengine-api.git@v0.1.384#egg=earthengine-api&subdirectory=python",
        )

    test_files = session.posargs or ["tests"]
    session.run("pytest", "--color=yes", "--cov", "--cov-report=xml", *test_files)


@nox.session(reuse_venv=False)
def test_gee(session):
    """Run GEE smoke tests. Requires EARTHENGINE_* credentials."""
    _preinstall_pysepal_api(session)
    session.install(".[test]")
    session.run("pip", "list")

    if "sepal-user" in session.virtualenv.location:
        session.run(
            "pip",
            "install",
            "git+https://github.com/openforis/earthengine-api.git@v0.1.384#egg=earthengine-api&subdirectory=python",
        )

    test_files = session.posargs or ["tests"]
    session.run("pytest", "-m", "gee", "--color=yes", "-vv", *test_files)


@nox.session(name="clean_gee_assets", reuse_venv=True)
def clean_gee_assets(session):
    """Delete stale pysepal test assets from GEE. Dry-run by default; pass -- --yes to delete."""
    _preinstall_pysepal_api(session)
    session.install(".[test]")
    session.run("python", "-m", "tests._janitor", *session.posargs)


@nox.session(name="dead-fixtures", reuse_venv=True)
def dead_fixtures(session):
    """Check for dead fixtures items."""
    _preinstall_pysepal_api(session)
    session.install(".[test]")
    test_files = session.posargs or ["tests"]
    # Clear addopts ("-m 'not gee'") so the scan covers both test lanes;
    # otherwise every GEE fixture reports as unused.
    session.run("pytest", "-o", "addopts=", "--dead-fixtures", *test_files)


@nox.session(reuse_venv=True)
def bin(session):
    """Run all the bin methods to validate the conda recipe."""
    _preinstall_pysepal_api(session)
    session.install(".")
    session.run("module_deploy", "--help")
    session.run("module_factory", "--help")
    session.run("module_l10n", "--help")
    session.run("module_theme", "--help")
    session.run("module_venv", "--help")
    session.run("activate_venv", "--help")
    session.run("sepal_ipyvuetify", "--help")


@nox.session(reuse_venv=True)
def docs(session):
    """Build the documentation."""
    _preinstall_pysepal_api(session)
    session.install(".[doc]")
    # patch version in nox instead of pyproject to avoid blocking conda releases
    session.run("rm", "-rf", "docs/source/modules", external=True)
    session.run("rm", "-rf", "docs/build/html", external=True)

    # build the api doc files
    templates = "docs/source/_templates/apidoc"
    modules = "docs/source/modules"
    session.run("sphinx-apidoc", f"--templatedir={templates}", "-o", modules, "pysepal")

    # build the documentation
    source = "docs/source"
    html = "docs/build/html"
    session.run("sphinx-build", "-b", "html", source, html, "-w", "warnings.txt")

    # check for untracked documentation warnings
    session.run("python", "tests/check_warnings.py")


@nox.session(reuse_venv=True)
def mypy(session):
    """Run a mypy check of the lib."""
    _preinstall_pysepal_api(session)
    session.install(".[dev]")
    test_files = session.posargs or ["pysepal"]
    session.run(
        "mypy",
        "--scripts-are-modules",
        "--ignore-missing-imports",
        "--install-types",
        "--non-interactive",
        "--disable-error-code",
        "func-returns-value",
        "--warn-redundant-casts",
        *test_files,
    )
