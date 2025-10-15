from typing import List

from aicssegmentation.workflow import WorkflowDefinition
import cv2
import numpy as np
from qtpy.QtWidgets import (
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QWidget,
)
from qtpy.QtGui import QIcon, QPixmap, QImage
from qtpy import QtCore
from qtpy.QtCore import Signal

from napari_allencell_segmenter.widgets.form import Form, FormRow
from napari_allencell_segmenter._style import PAGE_CONTENT_WIDTH, Style


class WorkflowThumbnails(QWidget):
    """
    A widget containing thumbnail images for workflows.

    Params:
        workflow_defs (List[WorkflowDefinition]): List of
            workflow definitions to display as buttons
    """

    workflowSelected = Signal(str)  # signal: emitted when a workflow is selected

    def __init__(self, workflows: List[WorkflowDefinition] = None):
        super().__init__()
        self._workflow_definitions = workflows

        if workflows is not None:
            self.load_workflows(workflows)

    @property
    def workflow_definitions(self) -> List[WorkflowDefinition]:
        return self._workflow_definitions

    def load_workflows(self, workflows: List[WorkflowDefinition]):
        """
        Load given Workflow definitions and rebuild the grid
        """
        if workflows is None:
            raise ValueError("workflows")

        self._workflow_definitions = workflows

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)  # reset setLayout

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

            # TODO: We need a way to a) track dimension order if present in metadata and b) try to guess dimension order
            color_channel_size: int = min(np.shape(workflow.thumbnail_pre))
            min_index: int = np.shape(workflow.thumbnail_pre).index(color_channel_size)

            # If RGBA convert to grayscale
            if len(workflow.thumbnail_pre.shape) > 2:
                # cv2 expects color channel dim to be last index
                pre = cv2.cvtColor(np.moveaxis(workflow.thumbnail_pre, min_index, -1), cv2.COLOR_RGBA2GRAY)
            if len(workflow.thumbnail_post.shape) > 2:
                # cv2 expects color channel dim to be last index
                post = cv2.cvtColor(np.moveaxis(workflow.thumbnail_post, min_index, -1), cv2.COLOR_RGBA2GRAY)
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
            button.setToolTip(workflow.name)

            button.setEnabled(False)
            button.setObjectName(workflow.name)
            button.clicked.connect(self._workflow_button_clicked)

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
        for button in self.findChildren(QPushButton):
            button.setEnabled(True)

    def _disable_buttons(self):
        """
        Disable all buttons in the widget
        """
        for button in self.findChildren(QPushButton):
            button.setDisabled(True)

    def _workflow_button_clicked(self, checked: bool):
        """
        Handle click of a workflow thumbnail button
        """
        self.workflowSelected.emit(self.sender().objectName())
