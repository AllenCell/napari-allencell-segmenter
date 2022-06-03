from qtpy.QtWidgets import QComboBox

from napari_allencell_segmenter.widgets.form import FormRow


class UiUtils:
    @staticmethod
    def dropdown_row(label: str, placeholder: str = None, default: str = None, options=None, enabled=False) -> FormRow:
        """
        Given the contents of a dropdown and a label, return a FormRow containing
        a label and a QComboBox widget that can be used with the custom Form widget
        """
        dropdown = QComboBox()
        dropdown.setDisabled(not enabled)
        dropdown.setStyleSheet("QComboBox { combobox-popup: 0; }")
        if placeholder is not None:
            dropdown.addItem(placeholder)
        if options is not None:
            str_options = [str(option) for option in options]
            dropdown.addItems(str_options)
        if placeholder is None and default is not None and options is not None:
            default_index = options.index(default)
            dropdown.setCurrentIndex(default_index)

        return FormRow(label, dropdown)
