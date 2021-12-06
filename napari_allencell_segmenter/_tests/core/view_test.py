import pytest

from qtpy.QtWidgets import QFrame
from napari_allencell_segmenter.core.view import View, ViewTemplate


class FakeTemplate(ViewTemplate):
    def load(self):
        pass

    def get_container(self) -> QFrame:
        return QFrame()


class FakeView(View):
    def load(self):
        pass


class TestView:
    def test_init_throws_with_bad_template(self):
        with pytest.raises(TypeError):
            FakeView(template_class=object)

    def test_template(self):
        view = FakeView(template_class=FakeTemplate)
        assert view.template is not None
        assert view.has_template()
        assert isinstance(view.template, FakeTemplate)

    def test_no_template(self):
        view = FakeView()
        assert view.template is None
        assert not view.has_template()
