"""
Global stylesheet

Qt stylesheet reference: https://doc.qt.io/qtforpython-5/overviews/stylesheet-syntax.html
Examples: https://doc.qt.io/qt-5/stylesheet-examples.html#customizing-specific-widgets
"""

STYLESHEET = (
    """
    QComboBox:disabled { 
        background-color: #333941;
        color: #7c848a;
    }

    QFrame#page {
        margin-right: 20px;
    }

    QLabel {
        font-size: 14px;
    }

    QLabel#header {
        font-size: 12px;
        margin-bottom: 0.5em;
    }

    QLabel#workflowSelectionTitle {
        font-weight: bold;
    }

    #columnLabels QLabel {
        font-size: 12px;
        font-weight: bold;
    }

    #columnLabelsDisabled QLabel {
        font-size: 12px;
        font-weight: bold;
        color: #7c848a;
    }

    QLabel#btnInstructionsDisabled, QLabel#step3InstructionsDisabled {
        color: #7c848a;
    }

    QPushButton:disabled { 
        background-color: #333941;
    }
    """
)
