class Library:
    def __init__(self, server_id: str = None, library: str = None, installed: bool = None) -> None:
        self.server_id = server_id
        self.library = library
        self.installed = installed