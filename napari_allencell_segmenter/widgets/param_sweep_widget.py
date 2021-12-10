
from qtpy.QtWidgets import QDialog

from typing import Dict, Any
from widgets.form import FormRow


class ParamSweepWidget(QDialog):
    """
    A dialog box containing a workflow finished message. Also includes a button to open the output folder
    and a button to close the dialog box

    Params:
        output_folder (Path):       The output folder to open when the corresponding button is clicked by the user.
    """

    def __init__(self, param_set: Dict[str, Any]):
        super().__init__()

        self._param_set = param_set

    def _param_set_to_form_rows(self):
