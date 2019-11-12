class InvalidUUIDError(Exception):
    status_code = 400

    def __init__(self, message="An invalid UUID was received"):
        Exception.__init__(self)
        self.message = message

    def to_dict(self):
        return dict(title="Invalid UUID", status=400, detail=self.message)
