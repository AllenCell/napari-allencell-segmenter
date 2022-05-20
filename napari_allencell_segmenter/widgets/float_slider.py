from qtpy.QtWidgets import QDoubleSpinBox
import magicgui.widgets


class FloatSlider(magicgui.widgets.FloatSlider):
    """
    Custom FloatSlider widget
    This class is used to avoid accessing the underlying FloatSlider's private API
    from other parts of the plugin
    TODO remove once features are exposed on the magicgui FloatSlider
         see https://github.com/napari/magicgui/issues/226
    """

    def setDecimals(self, precision: int):
        """
        Set decimal precision (number of decimals) for the slider
        """
        spinbox: QDoubleSpinBox = self._widget._readout_widget
        spinbox.setDecimals(precision)
