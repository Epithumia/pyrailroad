class ParseException(Exception):
    def __init__(self, msg: str, *args: object) -> None:
        super().__init__(msg, *args)
        self.msg = msg
