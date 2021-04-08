from PyQt5.QtWidgets import QComboBox

from napari_aicssegmentation.widgets.form import FormRow


def dropdown_row(number: int, placeholder: str, enabled=False) -> FormRow:
    """
    Given the contents of a dropdown and a number for the label, return a label and a QComboBox
    widget that can be used to create a row in a QFormLayout
    """
    label = f"{number}."

    dropdown = QComboBox()
    dropdown.addItem(placeholder)
    dropdown.setDisabled(not enabled)

    return FormRow(label, dropdown)
