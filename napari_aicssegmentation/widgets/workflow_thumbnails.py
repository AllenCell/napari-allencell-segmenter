from PyQt5.QtWidgets import (
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from PyQt5.QtGui import QIcon, QPixmap, QImage

from PyQt5.QtCore import QSize
import numpy as np
import cv2
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

    def __init__(self, workflow_defs):
        super().__init__()
        self.buttons = list()

        layout = QVBoxLayout()
        self.enabled = False
        self.setLayout(layout)
        self.add_buttons(workflow_defs)

    def add_buttons(self, workflows: List[WorkflowDefinition]):
        """
        Add all buttons given a List of WorkflowDefinitions
        """
        for workflow in workflows:
            if not isinstance(workflow, str):
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
                    QImage(
                        image_stitched.data, image_stitched.shape[1], image_stitched.shape[0], QImage.Format_Indexed8
                    )
                )
                button.setIcon(QIcon(image))
                button.setIconSize(QSize(PAGE_CONTENT_WIDTH - 40, 200))
                button.setFixedSize(PAGE_CONTENT_WIDTH, 200)

                button.setEnabled(False)

                self.layout().addWidget(button)

    def enable_buttons(self):
        """
        Enable all buttons in the widget
        """
        for ui_element in self.layout().parent().children():
            if isinstance(ui_element, QPushButton):
                ui_element.setEnabled(True)

    def disable_buttons(self):
        """
        Disable all buttons in the widget
        """
        for ui_element in self.layout().parent().children():
            if isinstance(ui_element, QPushButton):
                ui_element.setEnabled(False)
