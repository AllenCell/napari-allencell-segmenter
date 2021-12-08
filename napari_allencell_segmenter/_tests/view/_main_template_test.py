from napari_allencell_segmenter.view._main_template import MainTemplate
from qtpy.QtWidgets import QFrame


class TestMainTemplate:
    def test_get_container(self):
        template = MainTemplate()
        template.load()
        assert template.get_container() is not None
        assert isinstance(template.get_container(), QFrame)
