try:
    from ._version import version as __version__
except ImportError:
    __version__ = "unknown"

from ._dock_widget import napari_experimental_provide_dock_widget  # noqa: F401

# Do not edit this string manually, always use bumpversion
# Details in CONTRIBUTING.md
__version__ = "1.1.3"
