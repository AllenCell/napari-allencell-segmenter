from napari_allencell_segmenter.widgets.file_input import FileInput, FileInputMode


class TestFileInput:
    def test_properties(self):
        expected_mode = FileInputMode.DIRECTORY
        expected_filter = "(*.json)"

        widget = FileInput(mode=expected_mode, filter=expected_filter)
        assert widget.mode == expected_mode
        assert widget.filter == expected_filter
