class NotFoundError(Exception):
    status_code = 404

    def __init__(self, message="The requested resource does not exist"):
        super().__init__()
        self.message = message

    def to_dict(self):
        return dict(title="Not Found", status=404, detail=self.message)
