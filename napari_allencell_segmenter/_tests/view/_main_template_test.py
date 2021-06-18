from napari_allencell_segmenter.view._main_template import MainTemplate
from PyQt5.QtWidgets import QFrame


class TestMainTemplate:
    def test_get_container(self):
        template = MainTemplate()
        template.load()
        assert template.get_container() is not None
        assert isinstance(template.get_container(), QFrame)
