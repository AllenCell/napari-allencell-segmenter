""" Dimensions """
PAGE_WIDTH = 440
PAGE_CONTENT_WIDTH = PAGE_WIDTH - 40
WORKFLOW_BUTTON_HEIGHT = 200


"""
Global stylesheet

Qt stylesheet reference: https://doc.qt.io/qtforpython-5/overviews/stylesheet-syntax.html
Examples: https://doc.qt.io/qt-5/stylesheet-examples.html#customizing-specific-widgets
"""
STYLESHEET = (
    """
    QComboBox:disabled { 
        background-color: #333941;
        color: #7C848A;
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
        color: #44494c;
    }

    QLabel#btnInstructionsDisabled, QLabel#step3InstructionsDisabled {
        color: #44494c;
    }

    QPushButton:disabled { 
        background-color: #333941;
    }

    CollapsiblePanel .QFrame {
        background-color: #5a626d;
        border-radius: 2px;
        border-color: #6d7075;
        border-width: 0.5px;
        border-style: solid;
    }

    CollapsiblePanel QFrame:disabled {
        background-color: #333942;
        border-radius: 2px;
        border-width: 0px;
        color: #7C848A;
    }

    CollapsiblePanel .QFrame#contentBox {
        background-color: #414852;
        border-top: 0px;
    }
    """
)
