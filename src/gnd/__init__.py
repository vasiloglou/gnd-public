"""GND runtime library: ORM model loading, population loading, and constraint checking."""

from importlib.metadata import PackageNotFoundError, version

#: The name this project is published and installed under. The import package and
#: the console script are both ``gnd``; only the distribution differs, because
#: ``gnd`` has been taken on PyPI since 2022 (D-01). It lives here rather than in
#: ``cli.py`` so the installer can read it without a service module importing the
#: controller.
DISTRIBUTION = "get-nick-done"

#: What ``resolve_version()`` reports when there is no installed metadata. It is
#: deliberately not a plausible-looking release number: a human reading
#: ``gnd --version`` in a bug report must be able to tell at a glance that the
#: binary came from an uninstalled checkout (D-02).
DEV_VERSION = "0.0.0.dev+unpackaged"

__all__ = ["DEV_VERSION", "DISTRIBUTION", "resolve_version"]


def resolve_version() -> str:
    """Version from installed distribution metadata, never from a literal.

    ``pyproject.toml`` is the single place a version number is written (D-02). A
    ``__version__`` constant plus ``dynamic = ["version"]`` was considered and
    rejected: it is a second place to forget.
    """
    try:
        return version(DISTRIBUTION)
    except PackageNotFoundError:
        return DEV_VERSION
