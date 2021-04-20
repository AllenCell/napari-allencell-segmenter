from aicssegmentation.workflow import WorkflowEngine, WorkflowStepCategory
from qtpy.QtGui import QPixmap
from qtpy.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QProgressBar,
    QPushButton,
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
from napari_aicssegmentation.util.directories import Directories
from napari_aicssegmentation._style import PAGE_CONTENT_WIDTH


@debug_class
class WorkflowStepsView(View):  # pragma: no-cover
    # _lbl_selected_workflow: QLabel

    def __init__(self, controller: IWorkflowStepsController):
        super().__init__(template_class=MainTemplate)

        if controller is None:
            raise ValueError("controller")
        self._controller = controller
        self.setObjectName("workflowStepsView")

        self.diagram = QLabel()
        self.confirmation_modal = QMessageBox()

        # TODO: replace this with connection to model (first page selection)
        engine = WorkflowEngine()
        self.workflow = engine.workflow_definitions[3]
        self.all_steps = self.workflow.steps

    def setup_ui(self):
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.setLayout(self.layout)

        # self._lbl_selected_workflow = QLabel()

        # Add all widgets
        self._add_workflow_title()
        self._add_progress_bar()
        self._add_workflow_steps(WorkflowStepCategory.PRE_PROCESSING)
        self._add_workflow_steps(WorkflowStepCategory.CORE)
        self._add_workflow_steps(WorkflowStepCategory.POST_PROCESSING)
        self.layout.addSpacing(20)
        self.layout.addStretch()
        self._add_bottom_buttons()

    def load_model(self, model: SegmenterModel):
        pass
        # self._lbl_selected_workflow.setText(f"Selected workflow: {model.active_workflow}")
        # self._lbl_selected_workflow.repaint()

    def _add_workflow_title(self):
        widget = QWidget()
        layout = QHBoxLayout()
        widget.setLayout(layout)

        # Make widgets
        workflow_name = QLabel(f"Workflow: {self.workflow.name}")
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
        self.layout.addWidget(widget)

    def _add_progress_bar(self):
        num_steps = len(self.workflow.steps)

        # Progress bar
        progress_bar = QProgressBar()
        progress_bar.setRange(0, num_steps)
        progress_bar.setValue(0)
        progress_bar.setTextVisible(False)
        self.layout.addWidget(progress_bar)

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
        self.layout.addWidget(progress_labels)

    def _add_workflow_steps(self, category: WorkflowStepCategory):
        # Add category label, e.g., "Preprocessing"
        category_label = QLabel(category.value.upper())
        category_label.setObjectName("categoryLabel")
        self.layout.addWidget(category_label)

        # Add a widget for all the steps in this category
        for step in filter(lambda step: step.category == category, self.all_steps):
            self.layout.addWidget(WorkflowStepWidget(step))

        self.layout.addSpacing(10)

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

        self.layout.addLayout(layout)

    #####################################################################
    # Event handlers
    #####################################################################

    def _btn_info_clicked(self, checked: bool):
        diagram_path = str(Directories.get_assets_dir() / "workflow_diagrams/sec61b_1.png")
        self.diagram.setPixmap(QPixmap(diagram_path))
        self.diagram.show()

    def _btn_close_clicked(self, checked: bool):
        prompt = (
            "<span>You are closing an in-progress Allen Cell & Structure Segmenter plugin workflow to return "
            "to the Workflow Selection screen.&nbsp;Your progress in this workflow will be lost.</span>"
        )
        
        self.confirmation_modal.setModal(True)
        self.confirmation_modal.setIcon(QMessageBox.Warning)
        self.confirmation_modal.setText(f"Workflow: {self.workflow.name}")
        self.confirmation_modal.setInformativeText(prompt)
        self.confirmation_modal.setStandardButtons(QMessageBox.Cancel)

        if len(self.confirmation_modal.buttons()) < 2:
            self.close_keep = self.confirmation_modal.addButton("Close workflow", QMessageBox.AcceptRole)

        self.confirmation_modal.exec()
        self._handle_modal_input(self.confirmation_modal.clickedButton())

    def _handle_modal_input(self, input):
        if input == self.close_keep:
            self._controller.navigate_back()

    def _btn_run_all_clicked(self, checked: bool):
        self._controller.navigate_back()
