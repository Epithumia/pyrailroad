class RRException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class ParseException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
