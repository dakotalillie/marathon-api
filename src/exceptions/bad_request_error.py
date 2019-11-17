class BadRequestError(Exception):
    status_code = 400

    def __init__(self, message="The requested operation could not be completed"):
        super().__init__()
        self.message = message

    def to_dict(self):
        return dict(title="Bad Request", status=400, detail=self.message)
