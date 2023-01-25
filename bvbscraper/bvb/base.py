import uuid


class BaseEntity:

    def __init__(self) -> None:
        self._UUID = str(uuid.uuid4())

    def __getattribute__(self, __name: str):
        return super().__getattribute__(__name)
