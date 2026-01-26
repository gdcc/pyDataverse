import nox

PYTHON_VERSIONS = ["3.9", "3.10", "3.11", "3.12", "3.13"]
PACKAGE = "src/pydataverse"
TESTS = "tests"


def install_with_poetry(session):
    """Install project and dev dependencies using Poetry inside the nox venv."""
    session.install("poetry")
    session.run("poetry", "install", "--no-interaction", external=True)


@nox.session
def test(session):
    """Run pytest with coverage."""
    install_with_poetry(session)
    session.run("pytest", "--cov", PACKAGE, "--cov-report=xml", TESTS)
    session.run("coverage", "xml")


@nox.session(python=PYTHON_VERSIONS)
def test_all(session):
    """Run pytest with coverage across multiple Python versions."""
    install_with_poetry(session)
    session.run("pytest", "--cov", PACKAGE, "--cov-report=xml", TESTS)
    session.run("coverage", "xml")


@nox.session
def lint(session):
    """Run ruff and black in check mode."""
    install_with_poetry(session)
    session.run("ruff", "check", ".")
    session.run("black", "--check", ".")


@nox.session
def format(session):
    """Run ruff and black in format mode."""
    install_with_poetry(session)
    session.run("ruff", "check", "--fix", PACKAGE, TESTS, ".")
    session.run("black", "--check", PACKAGE, TESTS)


@nox.session
def typecheck(session):
    """Run mypy and pyright type checking."""
    install_with_poetry(session)
    session.run("pyright", PACKAGE, TESTS)
    session.run("mypy", PACKAGE)


@nox.session
def build(session):
    """Build the package using Poetry (sdist + wheel)."""
    install_with_poetry(session)
    session.run("poetry", "build", external=True)
