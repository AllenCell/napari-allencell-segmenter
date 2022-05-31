from typing import List
import numpy as np

from aicssegmentation.workflow import WorkflowStepCategory
from qtpy.QtCore import Qt
from qtpy.QtGui import QImage, QPixmap
from qtpy.QtWidgets import (
    QFileDialog,
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

from napari_allencell_segmenter.model.segmenter_model import SegmenterModel
from napari_allencell_segmenter.controller._interfaces import IWorkflowStepsController
from napari_allencell_segmenter.core.view import View
from napari_allencell_segmenter.widgets.workflow_step_widget import WorkflowStepWidget
from napari_allencell_segmenter.view._main_template import MainTemplate
from napari_allencell_segmenter._style import PAGE_CONTENT_WIDTH


class WorkflowStepsView(View):  # pragma: no-cover
    window_workflow_diagram: QScrollArea
    modal_close_workflow: QMessageBox
    progress_bar: QProgressBar
    btn_workflow_info: QPushButton
    btn_run_all: QPushButton
    btn_save_workflow: QPushButton
    btn_close_keep: QPushButton

    def __init__(self, controller: IWorkflowStepsController):
        super().__init__(template_class=MainTemplate)

        if controller is None:
            raise ValueError("controller")
        self._controller = controller
        self.setObjectName("workflowStepsView")

    def load(self, model: SegmenterModel):
        self._workflow = model.active_workflow
        self._setup_ui()

    def _setup_ui(self):
        self._layout = QVBoxLayout()
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)
        self.setLayout(self._layout)

        # Add all widgets
        self._add_workflow_title()
        self._add_progress_bar()
        steps = 0
        steps = self._add_workflow_steps(WorkflowStepCategory.PRE_PROCESSING, steps)
        steps = self._add_workflow_steps(WorkflowStepCategory.CORE, steps)
        steps = self._add_workflow_steps(WorkflowStepCategory.POST_PROCESSING, steps)
        self._layout.addSpacing(20)
        self._layout.addStretch()
        self._add_bottom_buttons()
        self._setup_diagram_window()
        self._setup_close_workflow_window()

    def _add_workflow_title(self):
        widget = QWidget()
        layout = QHBoxLayout()
        widget.setLayout(layout)

        # Make widgets
        workflow_name = QLabel(f"Workflow: {self._workflow.workflow_definition.name}")
        self.btn_workflow_info = QPushButton("ⓘ")
        self.btn_workflow_info.setObjectName("infoButton")
        self.btn_workflow_info.clicked.connect(self._btn_info_clicked)

        # Add widgets and whitespace
        layout.addStretch()
        layout.addWidget(workflow_name)
        layout.addWidget(self.btn_workflow_info)
        layout.addStretch()
        layout.setSpacing(3)

        # Add to to main layout
        widget.setObjectName("workflowTitle")
        self._layout.addWidget(widget)

    def _add_progress_bar(self):
        num_steps = len(self._workflow.workflow_definition.steps)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, num_steps)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self._layout.addWidget(self.progress_bar)

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

    def _add_workflow_steps(self, category: WorkflowStepCategory, steps: int):
        # Add category label, e.g., "Preprocessing"
        category_label = QLabel(category.value.upper())
        category_label.setObjectName("categoryLabel")
        self._layout.addWidget(category_label)
        # Add a widget for all the steps in this category
        i = steps
        for step in filter(lambda step: step.category == category, self._workflow.workflow_definition.steps):
            if i == 0:
                self._layout.addWidget(WorkflowStepWidget(step, i, steps_view=self, enable_button=True))
            else:
                self._layout.addWidget(WorkflowStepWidget(step, i, steps_view=self, enable_button=False))
            i = i + 1

        self._layout.addSpacing(10)
        return i

    def _add_bottom_buttons(self):
        layout = QHBoxLayout()
        layout.setSpacing(5)

        btn_close_workflow = QPushButton("Close workflow")
        btn_close_workflow.setFixedWidth(120)
        btn_close_workflow.clicked.connect(self._btn_close_clicked)

        self.btn_save_workflow = QPushButton("Save workflow")
        self.btn_save_workflow.setFixedWidth(120)
        self.btn_save_workflow.clicked.connect(self._btn_save_workflow_clicked)

        self.btn_run_all = QPushButton("Run all")
        self.btn_run_all.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.btn_run_all.clicked.connect(self._btn_run_all_clicked)

        layout.addWidget(btn_close_workflow)
        layout.addWidget(self.btn_save_workflow)
        layout.addWidget(self.btn_run_all)

        self._layout.addLayout(layout)

    def _setup_diagram_window(self):
        self.window_workflow_diagram = QScrollArea()
        diagram = QLabel()
        # TODO: remove this when dimension order refactor happens
        color_channel_size: int = min(np.shape(self._workflow.workflow_definition.diagram_image))
        min_index: int = np.shape(self._workflow.workflow_definition.diagram_image).index(color_channel_size)

        img_data = np.moveaxis(self._workflow.workflow_definition.diagram_image, min_index, -1)
        img = QImage(img_data, img_data.shape[1], img_data.shape[0], QImage.Format.Format_RGB888)
        diagram.setPixmap(QPixmap(img).scaledToWidth(1000, Qt.TransformationMode.SmoothTransformation))

        self.window_workflow_diagram.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.window_workflow_diagram.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.window_workflow_diagram.setFixedWidth(1000)
        self.window_workflow_diagram.setMinimumHeight(800)
        self.window_workflow_diagram.setWidget(diagram)

    def _setup_close_workflow_window(self):
        self.modal_close_workflow = QMessageBox()

        prompt = (
            "<span>You are closing an in-progress Allen Cell & Structure Segmenter plugin workflow to return "
            "to the Workflow Selection screen.&nbsp;Your progress in this workflow will be lost.</span>"
        )

        self.modal_close_workflow.setModal(True)
        self.modal_close_workflow.setIcon(QMessageBox.Warning)
        self.modal_close_workflow.setText(f"Workflow: {self._workflow.workflow_definition.name}")
        self.modal_close_workflow.setInformativeText(prompt)
        self.modal_close_workflow.setStandardButtons(QMessageBox.Cancel)
        # Modal buttons
        self.btn_close_keep = self.modal_close_workflow.addButton("Close workflow", QMessageBox.AcceptRole)
        self.btn_close_keep.clicked.connect(self._btn_close_keep_clicked)

    def set_run_all_in_progress(self):
        self.btn_run_all.setText("Cancel")
        self.btn_run_all.clicked.disconnect()
        self.btn_run_all.clicked.connect(self._btn_run_all_cancel_clicked)

    def reset_run_all(self):
        self.progress_bar.setValue(0)
        self.btn_run_all.setText("Run all")
        self.btn_run_all.clicked.disconnect()
        self.btn_run_all.clicked.connect(self._btn_run_all_clicked)

    def reset_run_step(self):
        self.btn_run_all.setText("Run all")
        self.btn_run_all.clicked.disconnect()
        self.btn_run_all.clicked.connect(self._btn_run_all_clicked)

    def increment_progress_bar(self):
        value = self.progress_bar.value()
        self.progress_bar.setValue(value + 1)

    def set_progress_bar(self, i: int):
        self.progress_bar.setValue(i + 1)

    def _get_workflow_step_widgets(self) -> List[WorkflowStepWidget]:
        return self.findChildren(WorkflowStepWidget)

    def get_controller(self):
        return self._controller

    #####################################################################
    # Event handlers
    #####################################################################

    def _btn_info_clicked(self, checked: bool):
        self.window_workflow_diagram.show()

    def _btn_close_clicked(self, checked: bool):
        self.modal_close_workflow.exec()

    def _btn_close_keep_clicked(self, checked: bool):
        self._controller.close_workflow()

    def _btn_run_all_clicked(self, checked: bool):
        all_parameter_inputs = [w.get_parameter_inputs() for w in self._get_workflow_step_widgets()]
        self._controller.run_all(all_parameter_inputs)

    def _btn_run_all_cancel_clicked(self, checked: bool):
        self.btn_run_all.setText("Canceling...")
        self._controller.cancel_run_all()

    def _btn_save_workflow_clicked(self, checked: bool):
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            caption="Save workflow as...",
            filter="Json file (*.json)",
            directory="workflow.json",
            options=QFileDialog.Option.DontUseNativeDialog | QFileDialog.Option.DontUseCustomDirectoryIcons,
        )

        if file_path:
            steps = [w.get_workflow_step_with_inputs() for w in self._get_workflow_step_widgets()]
            self._controller.save_workflow(steps, file_path)

    def btn_run_clicked(self, step_index: int):
        parameters_for_step = self._get_workflow_step_widgets()[step_index].get_parameter_inputs()
        self._controller.run_step(step_index, parameters_for_step)

    def open_sweep_ui(self, step_index: int):
        params_for_step = self._get_workflow_step_widgets()[step_index].get_parameter_inputs()
        self._controller.open_sweep_ui(params_for_step, step_index)
