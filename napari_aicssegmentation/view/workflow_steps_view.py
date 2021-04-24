import numpy as np

from aicssegmentation.workflow import WorkflowStepCategory
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from napari_aicssegmentation.model.segmenter_model import SegmenterModel
from napari_aicssegmentation.util.debug_utils import debug_class
from napari_aicssegmentation.controller._interfaces import IWorkflowStepsController
from napari_aicssegmentation.core.view import View
from napari_aicssegmentation.widgets.workflow_step_widget import WorkflowStepWidget
from napari_aicssegmentation.view._main_template import MainTemplate
from napari_aicssegmentation._style import PAGE_CONTENT_WIDTH


@debug_class
class WorkflowStepsView(View):  # pragma: no-cover
    _workflow_diagram_scroll: QScrollArea
    _modal_close_workflow: QMessageBox
    _btn_close_keep: QPushButton

    def __init__(self, controller: IWorkflowStepsController):
        super().__init__(template_class=MainTemplate)

        if controller is None:
            raise ValueError("controller")
        self._controller = controller
        self.setObjectName("workflowStepsView")
        self.workflow_step_widgets = []

    def setup_ui(self):
        # TODO the setup_ui + load_model pattern does not work well for a complex page
        #      like this one that relies on the model to actually build the UI
        #      refactor into something more straightforward like a View.on_load(model) method
        #      that combines loading of the view + an optional model to pass in
        pass

    def _setup_ui(self):
        # Workaround for now - see TODO comment in setup_ui
        self._layout = QVBoxLayout()
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)
        self.setLayout(self._layout)

        # Add all widgets
        self._add_workflow_title()
        self._add_progress_bar()
        self._add_workflow_steps(WorkflowStepCategory.PRE_PROCESSING)
        self._add_workflow_steps(WorkflowStepCategory.CORE)
        self._add_workflow_steps(WorkflowStepCategory.POST_PROCESSING)
        self._layout.addSpacing(20)
        self._layout.addStretch()
        self._add_bottom_buttons()
        self._setup_diagram_window()
        self._setup_close_workflow_window()

    def load_model(self, model: SegmenterModel):
        # Workaround for now - see TODO comment in setup_ui
        self._workflow = model.active_workflow
        self._setup_ui()

    def _add_workflow_title(self):
        widget = QWidget()
        layout = QHBoxLayout()
        widget.setLayout(layout)

        # Make widgets
        workflow_name = QLabel(f"Workflow: {self._workflow.workflow_definition.name}")
        info = QPushButton("ⓘ")
        info.setObjectName("infoButton")
        info.clicked.connect(self._btn_info_clicked)

        # Add widgets and whitespace
        layout.addStretch()
        layout.addWidget(workflow_name)
        layout.addWidget(info)
        layout.addStretch()
        layout.setSpacing(3)

        # Add to to main layout
        widget.setObjectName("workflowTitle")
        self._layout.addWidget(widget)

    def _add_progress_bar(self):
        num_steps = len(self._workflow.workflow_definition.steps)

        # Progress bar
        progress_bar = QProgressBar()
        progress_bar.setRange(0, num_steps)
        progress_bar.setValue(0)
        progress_bar.setTextVisible(False)
        self._layout.addWidget(progress_bar)

        # Tick marks

        progress_labels = QLabel()
        progress_labels.setFixedWidth(PAGE_CONTENT_WIDTH)
        progress_labels.setObjectName("progressLabels")

        labels_layout = QHBoxLayout()
        labels_layout.setContentsMargins(5, 0, 5, 11)
        progress_labels.setLayout(labels_layout)

        for step in range(0, num_steps + 1):
            tick = QLabel("|")
            labels_layout.addWidget(tick)
            if step < num_steps:
                labels_layout.addStretch()
        self._layout.addWidget(progress_labels)

    def _add_workflow_steps(self, category: WorkflowStepCategory):
        # Add category label, e.g., "Preprocessing"
        category_label = QLabel(category.value.upper())
        category_label.setObjectName("categoryLabel")
        self._layout.addWidget(category_label)

        # Add a widget for all the steps in this category
        for step in filter(lambda step: step.category == category, self._workflow.workflow_definition.steps):
            widget = WorkflowStepWidget(step)
            self._layout.addWidget(widget)
            self.workflow_step_widgets.append(widget)

        self._layout.addSpacing(10)

    def _add_bottom_buttons(self):
        layout = QHBoxLayout()
        layout.setSpacing(5)

        btn_close_workflow = QPushButton("Close workflow")
        btn_close_workflow.setFixedWidth(120)
        btn_close_workflow.clicked.connect(self._btn_close_clicked)

        btn_run_all = QPushButton("Run all")
        btn_run_all.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        btn_run_all.clicked.connect(self._btn_run_all_clicked)

        layout.addWidget(btn_close_workflow)
        layout.addWidget(btn_run_all)

        self._layout.addLayout(layout)

    def _setup_diagram_window(self):
        self._workflow_diagram_scroll = QScrollArea()
        diagram = QLabel()
        img_data = np.moveaxis(self._workflow.workflow_definition.diagram_image, 0, -1)
        img = QImage(img_data, img_data.shape[1], img_data.shape[0], QImage.Format.Format_RGB888)
        diagram.setPixmap(QPixmap(img).scaledToWidth(1000, Qt.TransformationMode.SmoothTransformation))

        self._workflow_diagram_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self._workflow_diagram_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._workflow_diagram_scroll.setFixedWidth(1000)
        self._workflow_diagram_scroll.setMinimumHeight(800)
        self._workflow_diagram_scroll.setWidget(diagram)

    def _setup_close_workflow_window(self):
        self._modal_close_workflow = QMessageBox()

        prompt = (
            "<span>You are closing an in-progress Allen Cell & Structure Segmenter plugin workflow to return "
            "to the Workflow Selection screen.&nbsp;Your progress in this workflow will be lost.</span>"
        )

        self._modal_close_workflow.setModal(True)
        self._modal_close_workflow.setIcon(QMessageBox.Warning)
        self._modal_close_workflow.setText(f"Workflow: {self._workflow.workflow_definition.name}")
        self._modal_close_workflow.setInformativeText(prompt)
        self._modal_close_workflow.setStandardButtons(QMessageBox.Cancel)

        if len(self._modal_close_workflow.buttons()) < 2:
            self._btn_close_keep = self._modal_close_workflow.addButton("Close workflow", QMessageBox.AcceptRole)

    #####################################################################
    # Event handlers
    #####################################################################

    def _btn_info_clicked(self, checked: bool):
        self._workflow_diagram_scroll.show()

    def _btn_close_clicked(self, checked: bool):
        self._modal_close_workflow.exec()
        if self._modal_close_workflow.clickedButton() == self._btn_close_keep:
            self._controller.close_workflow()

    def _btn_run_all_clicked(self, checked: bool):
        all_parameter_inputs = []
        for widget in self.workflow_step_widgets:
            all_parameter_inputs.append(widget.parameter_inputs)

        self._controller.run_all_and_add_image(all_parameter_inputs)
