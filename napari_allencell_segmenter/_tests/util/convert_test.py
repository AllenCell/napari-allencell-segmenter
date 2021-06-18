import pytest

from napari_allencell_segmenter.util.convert import Convert


class TestConvert:
    @pytest.mark.parametrize("input", ["True", "true", "TRUE", "tRuE", " true ", 1, True])
    def test_to_boolean_true(self, input):
        assert Convert.to_boolean(input) == True

    @pytest.mark.parametrize("input", ["False", "false", "FALSE", "fAlSe", " false ", 0, False])
    def test_to_boolean_false(self, input):
        assert Convert.to_boolean(input) == False

    @pytest.mark.parametrize("input", ["abcdef", object(), 1234, None])
    def test_to_boolean_bad_input_throws(self, input):
        with pytest.raises(ValueError):
            Convert.to_boolean(input)
