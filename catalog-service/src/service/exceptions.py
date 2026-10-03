class NotFoundError(Exception):
    def __init__(self, entity: str):
        self.entity = entity


class ConflictError(Exception):
    def __init__(self, detail: str):
        self.detail = detail