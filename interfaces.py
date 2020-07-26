
class IAccount:
    def get_seed(self) -> bytes:
        return bytes()


class ITransaction:
    def serialize(self) -> bytes:
        return bytes()
