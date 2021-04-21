import numpy as np
import cv2

from PyQt5.QtWidgets import (
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from PyQt5.QtGui import QIcon, QPixmap, QImage
from PyQt5.QtCore import QSize
from napari_aicssegmentation._style import PAGE_CONTENT_WIDTH
from aicssegmentation.workflow import WorkflowDefinition
from typing import List


class WorkflowThumbnails(QWidget):

    """
    A widget containing thumbnail images for workflows.

    Params:
        workflow_defs (List[WorkflowDefinition]): List of
            workflow definitions to display as buttons
    """

    def __init__(self, workflow_defs: List[WorkflowDefinition] = None):
        super().__init__()

        if workflow_defs is not None:
            self.load_workflows(workflow_defs)

    def load_workflows(self, workflows: List[WorkflowDefinition]):
        """
        Load given Workflow definitions and rebuild the grid
        """
        if workflows is None:
            raise ValueError("workflows")
        self._workflows = workflows
        self._add_buttons(workflows)

    def _add_buttons(self, workflows: List[WorkflowDefinition]):
        """
        Add all buttons given a List of WorkflowDefinitions
        """
        self.setLayout(QVBoxLayout())  # reset layout

        for workflow in workflows:
            # Some images are RGBA and others are Grayscale
            # TODO?: convert all images to RBGA
            pre: np.ndarray = workflow.thumbnail_pre
            post: np.ndarray = workflow.thumbnail_post
            # If RGBA convert to grayscale
            if len(workflow.thumbnail_pre.shape) > 2:
                # cv2 expects color channel dim to be last index
                pre = cv2.cvtColor(np.moveaxis(workflow.thumbnail_pre, 0, -1), cv2.COLOR_RGBA2GRAY)
            if len(workflow.thumbnail_post.shape) > 2:
                # cv2 expects color channel dim to be last index
                post = cv2.cvtColor(np.moveaxis(workflow.thumbnail_post, 0, -1), cv2.COLOR_RGBA2GRAY)
            # Stitch Image
            image_stitched: np.ndarray = np.hstack([pre, post])
            button: QPushButton = QPushButton("")
            # Get np image into QPixmap
            image: QPixmap = QPixmap(
                QImage(image_stitched.data, image_stitched.shape[1], image_stitched.shape[0], QImage.Format_Indexed8)
            )
            button.setIcon(QIcon(image))
            button.setIconSize(QSize(PAGE_CONTENT_WIDTH - 40, 200))
            button.setFixedSize(PAGE_CONTENT_WIDTH, 200)

            button.setEnabled(False)

            self.layout().addWidget(button)

    def setEnabled(self, enabled: bool) -> None:
        super().setEnabled(enabled)
        if enabled:
            self._enable_buttons()
        else:
            self._disable_buttons()

    def _enable_buttons(self):
        """
        Enable all buttons in the widget
        """
        for ui_element in self.layout().parent().children():
            if isinstance(ui_element, QPushButton):
                ui_element.setEnabled(True)

    def _disable_buttons(self):
        """
        Disable all buttons in the widget
        """
        for ui_element in self.layout().parent().children():
            if isinstance(ui_element, QPushButton):
                ui_element.setEnabled(False)
