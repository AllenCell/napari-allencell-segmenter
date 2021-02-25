from typing import Callable
from qtpy.QtWidgets import QLayout, QPushButton, QLabel

class MppView:
    # Events
    on_gaussian_blur_clicked: Callable

    def __init__(self, layout: QLayout):
        if layout is None:
            raise ValueError("layout")
        self._layout = layout        

    def present(self):
        btn = QPushButton("Gaussian kernel size = 3.0")
        btn.clicked.connect(self.on_gaussian_blur_clicked)

        desc = QLabel("Click button to smooth the current viewport image, higher numbers blur more. Result is displayed as a new channel.")
        desc.setWordWrap(True)
        
        self._layout.addWidget(desc)
        self._layout.addWidget(btn)       


