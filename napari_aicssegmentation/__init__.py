try:
    from ._version import version as __version__
except ImportError:
    __version__ = "unknown"


from ._writer import napari_get_writer, napari_write_image  # NOQA F401
from ._dock_widget import napari_experimental_provide_dock_widget  # NOQA F401

# Do not edit this string manually, always use bumpversion
# Details in CONTRIBUTING.md
__version__ = "0.0.0"
