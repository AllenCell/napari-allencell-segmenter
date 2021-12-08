import magicgui.widgets

from typing import List, NamedTuple, Union
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QFormLayout, QLabel, QWidget


class FormRow(NamedTuple):
    label: Union[str, QLabel]
    widget: Union[QWidget, magicgui.widgets.Widget]


class Form(QFormLayout):
    """
    A nicely formatted form layout.

    Inputs:
        rows:       List of FormRow
        margins:    Tuple of 4 numbers representing left, top, right, and bottom margins for
                    the form's contents. Qt defaults to (11, 11, 11, 11).
    """

    def __init__(self, rows: List[FormRow], margins=(0, 5, 11, 0)):
        super().__init__()
        self.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        self.setFormAlignment(Qt.AlignLeft)
        self.setLabelAlignment(Qt.AlignLeft)
        left, top, right, bottom = margins
        self.setContentsMargins(left, top, right, bottom)

        for row in rows:
            widget = row.widget
            if not isinstance(row.widget, QWidget):
                widget = row.widget.native
            self.addRow(row.label, widget)
