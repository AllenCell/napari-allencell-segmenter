from PyQt5.QtWidgets import QComboBox

from napari_aicssegmentation.widgets.form import FormRow


class UiUtils:
    @staticmethod
    def dropdown_row(label: str, placeholder: str, options=None, enabled=False) -> FormRow:
        """
        Given the contents of a dropdown and a label, return a FormRow containing
        a label and a QComboBox widget that can be used with the custom Form widget
        """
        dropdown = QComboBox()
        dropdown.addItem(placeholder)
        dropdown.setDisabled(not enabled)

        if options is None:
            options = []
        else:
            for option in options:
                dropdown.addItem(option)

        return FormRow(label, dropdown)
