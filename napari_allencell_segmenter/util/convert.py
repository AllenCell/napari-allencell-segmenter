class Convert:
    """
    Conversion utility functions
    """

    @staticmethod
    def to_boolean(value: object) -> bool:
        """
        Convert the given value into a Boolean, if given a convertible representation
        Valid representations include:
        - boolean value
        - string representation like "true" or "false"
        - integer binary representation 1 (True) or 0 (False)

        inputs:
            value: the value to convert
        """
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
            str_val = value.lower().strip()
            if str_val == "true":
                return True
            if str_val == "false":
                return False

        raise ValueError(f"Can't convert value {repr(value)} to boolean. Bad object type or representation.")
