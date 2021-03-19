"""
Global stylesheet

Qt stylesheet reference: https://doc.qt.io/qtforpython-5/overviews/stylesheet.html
Examples: https://doc.qt.io/qt-5/stylesheet-examples.html#customizing-specific-widgets
"""

STYLESHEET = (
    """
    QFrame#page {
        margin-right: 20px;
    }

    QLabel {
        font-size: 16px;
        margin-top: 1em;
    }

    QLabel#title {
        font-weight: bold;
        font-size: 20px;
        margin-top: 0px;
    }

    QLabel#columnLabels {
        font-size: 12px;
        font-weight: bold;
    }
    """
)
