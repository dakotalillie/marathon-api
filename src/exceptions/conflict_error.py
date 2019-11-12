class ConflictError(Exception):
    status_code = 409

    def __init__(
        self, message="The requested operation could not be completed due to a conflict"
    ):
        Exception.__init__(self)
        self.message = message

    def to_dict(self):
        return dict(title="Conflict", status=409, detail=self.message)

