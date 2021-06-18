from napari_allencell_segmenter.widgets.warning_message import WarningMessage


class TestWarningMessage:
    def test_get_message(self):
        expected_message = "Hello World!"
        widget = WarningMessage(expected_message)
        assert widget.message == expected_message
        assert widget.getMessage() == expected_message

    def test_set_message(self):
        old_message = "Warning"
        widget = WarningMessage(old_message)
        assert widget.message == old_message
        new_message = "Hello World!"
        widget.setMessage(new_message)
        assert widget.message == new_message
