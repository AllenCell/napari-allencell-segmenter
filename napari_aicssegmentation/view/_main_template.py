from napari_aicssegmentation.core.view import ViewTemplate
from PyQt5.QtWidgets import QFrame, QVBoxLayout, QScrollArea, QLabel
from PyQt5 import QtCore

from napari_aicssegmentation._style import (
    PAGE_WIDTH,     
    STYLESHEET
)

class MainTemplate(ViewTemplate):
    def __init__(self):
        super().__init__()
        self._container = QFrame()

    def get_container(self) -> QFrame:
        return self._container
    
    def setup_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.setStyleSheet(STYLESHEET)
        
        # Page        
        page = QFrame()
        page.setObjectName("page")
        #page.setFixedWidth(PAGE_WIDTH)        
        page.setLayout(QVBoxLayout())
        layout.addWidget(page)

        # Scroll
        scroll = QScrollArea()
        scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
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
        page.layout().addWidget(self._container)
        page.layout().addStretch()