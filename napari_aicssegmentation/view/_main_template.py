from napari_aicssegmentation.core.view import ViewTemplate
from PyQt5.QtWidgets import QFrame, QVBoxLayout, QScrollArea, QLabel
from PyQt5 import QtCore
from napari_aicssegmentation._style import Style

from napari_aicssegmentation.widgets.workflow_step_box import WorkflowStepBox
# from aicssegmentation.structure_wrapper.WorkflowStep import WorkflowStep


class MainTemplate(ViewTemplate):
    def __init__(self):
        super().__init__()
        self._container = QFrame()
        self._container.setObjectName("mainContainer")

    def get_container(self) -> QFrame:
        return self._container

    def setup_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.setStyleSheet(Style.get_stylesheet("main.qss"))

        # Page
        page = QFrame()
        page.setObjectName("page")
        page.setLayout(QVBoxLayout())
        page.layout().setContentsMargins(0, 0, 0, 0)
        layout.addWidget(page)

        # Scroll
        scroll = QScrollArea()
        scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)  # ScrollBarAsNeeded
        scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        scroll.setWidgetResizable(True)
        scroll.setWidget(page)
        layout.addWidget(scroll)

        # Header
        header = QLabel(
            """
            <span>
                <b>ALLEN CELL & STRUCTURE SEGMENTER</b><br/>
                v1.0 supports static 3D images only
            </span>
            """
        )
        header.setObjectName("header")
        header.setAlignment(QtCore.Qt.AlignCenter)
        page.layout().addWidget(header)

        # Container
        self._container.setLayout(QVBoxLayout())
        self._container.layout().setContentsMargins(0, 0, 0, 0)
        page.layout().addWidget(self._container)
        page.layout().addStretch()

        test_workflow_step = dict()
        test_workflow_step["display_name"] = "intensity_normalization"
        test_workflow_step["function"] = {"parameters": [3, 15]}
        # test_workflow_step = WorkflowStep(test_workflow_step)

        page.layout().addWidget(WorkflowStepBox(test_workflow_step))  # Test code

        test_workflow_step = dict()
        test_workflow_step["display_name"] = "intensity_normalization_with_bound"
        test_workflow_step["function"] = {"parameters": [3, 15]}
        # test_workflow_step = WorkflowStep(test_workflow_step)
        page.layout().addWidget(WorkflowStepBox(test_workflow_step))
        test_workflow_step = dict()
        test_workflow_step["display_name"] = "size_filter"
        test_workflow_step["function"] = {"parameters": [1, 2]}
        # test_workflow_step = WorkflowStep(test_workflow_step)
        page.layout().addWidget(WorkflowStepBox(test_workflow_step))
