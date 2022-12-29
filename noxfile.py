import nox


@nox.session(reuse_venv=True)
def lint(session):
    session.install("pre-commit")
    session.run("pre-commit", "run", "--a", *session.posargs)


@nox.session(python=["3.7", "3.8", "3.9", "3.10"])  # , reuse_venv=True)
def test(session):
    session.install(".[test]")
    test_files = session.posargs or ["tests"]
    session.run("pytest", "--color=yes", *test_files)


@nox.session(reuse_venv=True)
def docs(session):
    session.install(".[doc]")
    session.run(
        "sphinx-apidoc",
        "--force",
        "--module-first",
        "--templatedir=docs/source/_templates/apidoc",
        "-o",
        "docs/source/modules",
        "./sepal_ui",
    )
    session.run("sphinx-build", "-b", "html", "docs/source", "build")


@nox.session(name="docs-live", reuse_venv=False)
def docs_live(session):
    session.install(".[doc]")
    session.run(
        "sphinx-apidoc",
        "--force",
        "--module-first",
        "--templatedir=docs/source/_templates/apidoc",
        "-o",
        "docs/source/modules",
        "./sepal_ui",
    )
    session.run("sphinx-autobuild", "-b", "html", "docs/source", "build")


@nox.session(name="mypy", reuse_venv=True)
def mypy(session):
    session.install(".[dev]")
    test_files = session.posargs or ["sepal_ui"]
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
