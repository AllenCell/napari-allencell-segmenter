class Convert:
    """
    Conversion utility functions
    """

    @staticmethod
    def to_boolean(value: object):
        if value is None:
            raise ValueError("Can't convert NoneType to boolean")

        if isinstance(value, bool):
            return value

        if isinstance(value, int):
            if value == 1:
                return True
            if value == 0:
                return False

        if isinstance(value, str):
            str_val = value.lower()
            if str_val == "true":
                return True
            if str_val == "false":
                return False

        raise ValueError(f"Can't convert value {repr(value)} to boolean. Bad object type or representation.")
