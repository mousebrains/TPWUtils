"""TPWUtils - A collection of Python 3 utilities."""

from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("TPWUtils")
except PackageNotFoundError:
    __version__ = "unknown"

__all__ = [
    "Credentials",
    "GreatCircle",
    "INotify",
    "Logger",
    "SingleInstance",
    "Thread",
    "install",
    "loadAndExecuteSQL",
]
