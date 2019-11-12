class ForbiddenError(Exception):
    status_code = 403

    def __init__(self, message="The requested operation is forbidden"):
        super().__init__()
        self.message = message

    def to_dict(self):
        return dict(title="Forbidden", status=403, detail=self.message)
