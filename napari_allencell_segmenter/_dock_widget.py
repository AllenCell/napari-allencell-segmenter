# Hook specifications: https://napari.org/docs/dev/plugins/hook_specifications.html
import napari

from napari_allencell_segmenter.core.application import Application
from qtpy.QtWidgets import QWidget, QVBoxLayout, QSizePolicy

"""
The class name here gets converted to title case and gets displayed as both the title 
of the plugin window and the title displayed in the app menu dropdown.
"""


class WorkflowEditorWidget(QWidget):  # pragma: no-cover
    def __init__(self, viewer: "napari.viewer.Viewer"):
        super().__init__()
        self._viewer = viewer
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.MinimumExpanding)
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self._application = Application(viewer, self.layout())
        self._application.router.workflow_selection()  # Initialize first screen


class BatchProcessingWidget(QWidget):
    def __init__(self, viewer: "napari.viewer.Viewer"):
        super().__init__()
        self._viewer = viewer
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.MinimumExpanding)
        self.setLayout(QVBoxLayout())
        self._application = Application(viewer, self.layout())
        self._application.router.batch_processing()  # Initialize first screen
