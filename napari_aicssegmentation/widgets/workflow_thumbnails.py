import numpy as np
import cv2

from PyQt5.QtWidgets import (
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QWidget,
)
from PyQt5.QtGui import QIcon, QPixmap, QImage
from PyQt5 import QtCore
from napari_aicssegmentation.widgets.form import Form, FormRow
from napari_aicssegmentation._style import PAGE_CONTENT_WIDTH, Style
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
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)  # reset setLayout

        if workflow_defs is not None:
            self.load_workflows(workflow_defs)

    def load_workflows(self, workflows: List[WorkflowDefinition]):
        """
        Load given Workflow definitions and rebuild the grid
        """
        if workflows is None:
            raise ValueError("workflows")
        self._workflows = workflows
        self._add_labels()
        self._add_buttons(workflows)
    
    def _add_labels(self):
        """
        Add widgets and set the layout for the Step 3 instructions and the workflow buttons
        """
        self.step_3_label = QLabel("3.")
        self.step_3_label.setAlignment(QtCore.Qt.AlignTop)
        self.step_3_instructions = QLabel(
            "Click a button below that most closely resembles your image channel to select & start a workflow"
        )
        self.step_3_instructions.setWordWrap(True)
        step_3 = QWidget()
        step_3.setLayout(Form([FormRow(self.step_3_label, self.step_3_instructions)], (0, 0, 11, 0)))

        self.step_3_instructions.setObjectName("step3InstructionsDisabled")
        self.layout().addWidget(step_3)

        # Row of text labeling the columns of workflow images
        self.column_labels = QWidget()
        column_layout = QHBoxLayout()
        column_layout.setContentsMargins(11, 11, 11, 0)
        self.column_labels.setLayout(column_layout)

        image_input_label = QLabel("Image input")
        image_input_label.setAlignment(QtCore.Qt.AlignCenter)
        segmentation_output_label = QLabel("Segmentation output")
        segmentation_output_label.setAlignment(QtCore.Qt.AlignCenter)
        self.column_labels.layout().addWidget(image_input_label)
        self.column_labels.layout().addWidget(segmentation_output_label)

        self.column_labels.setFixedWidth(PAGE_CONTENT_WIDTH)
        self.column_labels.setObjectName("columnLabelsDisabled")
        self.layout().addWidget(self.column_labels, alignment=QtCore.Qt.AlignCenter)

    def _add_buttons(self, workflows: List[WorkflowDefinition]):
        """
        Add all buttons given a List of WorkflowDefinitions
        """

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
            button.setIconSize(QtCore.QSize(PAGE_CONTENT_WIDTH - 40, 200))
            button.setFixedSize(PAGE_CONTENT_WIDTH, 200)

            button.setEnabled(False)

            self.layout().addWidget(button)

    def setEnabled(self, enabled: bool) -> None:
        super().setEnabled(enabled)
        if enabled:
            self.column_labels.setObjectName("columnLabels")
            self.step_3_instructions.setObjectName("step3Instructions")
            self.setStyleSheet(Style.get_stylesheet("main.qss"))

            self._enable_buttons()
        else:
            self.column_labels.setObjectName("columnLabelsDisabled")
            self.step_3_instructions.setObjectName("step3InstructionsDisabled")
            self.setStyleSheet(Style.get_stylesheet("main.qss"))

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