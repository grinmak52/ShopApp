class NotFoundError(Exception):
    def __init__(self, entity: str):
        self.entity = entity


class BadRequestError(Exception):
    def __init__(self, detail: str):
        self.detail = detail


class ServiceUnavailableError(Exception):
    def __init__(self, detail: str):
        self.detail = detail