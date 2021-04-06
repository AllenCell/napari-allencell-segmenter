from aicssegmentation.structure_wrapper_config.all_functions import get_all_functions


class Function():
    def __init__(self, config):
        self.function: str = config["function"]
        self.parameter_defaults = None
        if "parameter" in config:
            self.parameter_defaults = config["parameter"]

        self.parent = config["parent"]

        self.get_function_info(get_all_functions())


    def get_function_info(self, all_config):
        self.function_name = all_config["name"]
        self.module = all_config["module"]
        self.category = all_config["category"]
        self.param_info = all_config["parameter"]

