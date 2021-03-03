import logging
from napari_aicssegmentation.mvc.mpp_interfaces import IMppView
from qtpy.QtWidgets import QLayout, QPushButton, QLabel, QVBoxLayout
from .mpp_controller import MppController
from .mpp_model import MppModel
from ..ui_manager import UIManager
from ..util.debug_utils import debug_class
log = logging.getLogger(__name__)

@debug_class
class MppView(IMppView):
    _btn_gaussian_blur: QPushButton
    _lbl_description: QLabel
    _btn_show_layout: QPushButton
    _btn_hide_layout: QPushButton

    def __init__(self, ui_manager: UIManager):
        if ui_manager is None:
            raise ValueError("ui_manager")
                
        self._layout = QVBoxLayout()
        #ui_manager.base_layout.addLayout(self._layout)
        self._controller = MppController(ui_manager, self)
    
    # def setup_ui(self):        
    #     self._btn_gaussian_blur = QPushButton("Gaussian kernel size = 3.0")
    #     self._btn_gaussian_blur.clicked.connect(self.btn_gaussian_blur_clicked)

    #     self._lbl_description = QLabel("Click button to smooth the current viewport image, higher numbers blur more. Result is displayed as a new channel.")
    #     self._lbl_description.setWordWrap(True)
        
    #     self._layout.addWidget(self._lbl_description)
    #     self._layout.addWidget(self._btn_gaussian_blur)
        
    #     self._btn_show_layout = QPushButton("Show info")
    #     self._btn_show_layout.clicked.connect(self.btn_show_layout_clicked)
        
    #     self._btn_hide_layout = QPushButton("Hide info")
    #     self._btn_hide_layout.clicked.connect(self.btn_hide_layout_clicked)

    #     self._layout.addWidget(self._btn_show_layout)
    #     self._layout.addWidget(self._btn_hide_layout)

    def get_layout(self):
        return self._layout
        
    def setup_ui(self):        
        layout1 = QVBoxLayout()
        self._btn_gaussian_blur = QPushButton("Gaussian kernel size = 3.0")
        self._btn_gaussian_blur.clicked.connect(self.btn_gaussian_blur_clicked)

        self._lbl_description = QLabel("Click button to smooth the current viewport image, higher numbers blur more. Result is displayed as a new channel.")
        self._lbl_description.setWordWrap(True)
        
        layout1.addWidget(self._lbl_description)
        layout1.addWidget(self._btn_gaussian_blur)
        
        self._btn_show_layout = QPushButton("Show info")
        self._btn_show_layout.clicked.connect(self.btn_show_layout_clicked)
        
        self._btn_hide_layout = QPushButton("Hide info")
        self._btn_hide_layout.clicked.connect(self.btn_hide_layout_clicked)

        layout1.addWidget(self._btn_show_layout)
        layout1.addWidget(self._btn_hide_layout)
        self._layout.addLayout(layout1)

    # Event handlers        
    def btn_gaussian_blur_clicked(self, checked: bool):
        self._controller.run_gaussian_blur()

    def btn_show_layout_clicked(self, checked: bool):
        self._layout2 = QVBoxLayout()
        self._layout2.addWidget(QLabel("Hello world"))
        self._layout2.addWidget(QLabel("Some more text"))
        self._layout.addLayout(self._layout2)

    def btn_hide_layout_clicked(self, checked: bool):
        self._deleteItemsOfLayout(self._layout2)
        self._layout.removeItem(self._layout2)
        
    def _deleteItemsOfLayout(self, layout: QLayout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.setParent(None)
                else:
                    self._deleteItemsOfLayout(item.layout())        
