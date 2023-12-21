"""Inference engine."""
from importlib.metadata import PackageNotFoundError, version

__version__: str
try:
    # Change here if project is renamed and does not equal the package name
    _dist_name = __name__  # pylint:disable=invalid-name
    __version__ = version(_dist_name)
except PackageNotFoundError:
    __version__ = "0.0.0"
finally:
    del version, PackageNotFoundError
