from napari_aicssegmentation.core.view import View
from napari_aicssegmentation.controller._interfaces import IMppController
from napari_aicssegmentation.util.debug_utils import debug_class
from qtpy.QtWidgets import QLayout, QPushButton, QLabel, QVBoxLayout


@debug_class
class MppView(View):  # pragma: no-cover
    def __init__(self, controller: IMppController):
        if controller is None:
            raise ValueError("controller")
        
        self._controller = controller

    def setup_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        btn_gaussian_blur = QPushButton("Gaussian kernel size = 3.0")
        btn_gaussian_blur.clicked.connect(self._btn_gaussian_blur_clicked)

        lbl_description = QLabel(
            "Click button to smooth the current viewport image, higher numbers blur more. \
             Result is displayed as a new channel."
        )
        lbl_description.setWordWrap(True)

        btn_next = QPushButton("Next")
        btn_next.clicked.connect(self._btn_next_clicked)

        layout.addWidget(lbl_description)
        layout.addWidget(btn_gaussian_blur)
        layout.addWidget(btn_next)        

    # Event handlers
    def _btn_gaussian_blur_clicked(self, checked: bool):
        self._controller.run_gaussian_blur()

    def _btn_next_clicked(self, checked: bool):
        self._controller.navigate_next()
