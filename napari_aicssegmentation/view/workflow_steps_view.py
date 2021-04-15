from aicssegmentation.workflow import WorkflowEngine, WorkflowDefinition, WorkflowStep
from aicssegmentation.workflow.workflow_step import WorkflowStepCategory
from magicgui.widgets import FloatSlider, Slider
from qtpy.QtGui import QPixmap
from qtpy.QtWidgets import QHBoxLayout, QLabel, QProgressBar, QPushButton, QVBoxLayout, QWidget

from napari_aicssegmentation.model.segmenter_model import SegmenterModel
from napari_aicssegmentation.util.debug_utils import debug_class
from napari_aicssegmentation.controller._interfaces import IWorkflowStepsController
from napari_aicssegmentation.core.view import View
from napari_aicssegmentation.widgets.collapsible_box import CollapsibleBox
from napari_aicssegmentation.widgets.workflow_step_widget import WorkflowStepWidget
from napari_aicssegmentation.widgets.form import Form, FormRow
from napari_aicssegmentation.view._main_template import MainTemplate
from napari_aicssegmentation.util.directories import Directories
from napari_aicssegmentation.util.ui_utils import UiUtils
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

        # TODO: replace this with connection to model (first page selection)
        engine = WorkflowEngine()
        self.workflow = engine.workflow_definitions[0]
        self.all_steps = self.workflow.steps

    def setup_ui(self):
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.setLayout(self.layout)

        # self._lbl_selected_workflow = QLabel()

        btn_run_all = QPushButton("Run all")
        btn_run_all.clicked.connect(self._btn_back_clicked)

        # Add all widgets
        self._add_workflow_title()
        self._add_progress_bar()
        self._add_workflow_steps(WorkflowStepCategory.PRE_PROCESSING)
        self._add_workflow_steps(WorkflowStepCategory.CORE)
        self._add_workflow_steps(WorkflowStepCategory.POST_PROCESSING)
        self.layout.addSpacing(20)
        self.layout.addStretch()
        self.layout.addWidget(btn_run_all)

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
        progress_bar.setValue(num_steps - 2) # TODO: Replace with real value
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
        # steps = [
        #     {"number": 1, "name": "Intensity Normalization"},
        #     {"number": 2, "name": "Edge Preserving Smoothing"},
        # ]
        steps = []
        for step in self.all_steps:
            if step.category == category:
                steps.append(step)

        # Category label, e.g., "Preprocessing"
        category_label = QLabel(category.value.upper())
        category_label.setObjectName("categoryLabel")
        self.layout.addWidget(category_label)

        # TODO: replace this with the data-driven WorkflowStep widget
        for i, step in enumerate(steps):
            slider_1 = FloatSlider(value=2.5, min=0.5, max=30, step=0.5).native
            slider_1.setObjectName("slider")
            slider_2 = Slider(value=140, min=1, max=200, step=1).native
            slider_2.setObjectName("slider")
            row_1 = FormRow("Param 1", slider_1)
            row_2 = FormRow("Param 2", slider_2)

            row_3 = UiUtils.dropdown_row("Mode", "thick", enabled=True)
            row_3.widget.addItem("thin")

            content = Form([row_1, row_2, row_3], (11, 5, 5, 5))
            self.layout.addWidget(WorkflowStepWidget(step))

        self.layout.addSpacing(10)

    #####################################################################
    # Event handlers
    #####################################################################

    def _btn_back_clicked(self, checked: bool):
        self._controller.navigate_back()

    def _btn_info_clicked(self, checked: bool):
        self.diagram = QLabel()
        diagram_path = str(Directories.get_assets_dir() / "workflow_diagrams/sec61b_1.png")
        self.diagram.setPixmap(QPixmap(diagram_path))
        self.diagram.show()
