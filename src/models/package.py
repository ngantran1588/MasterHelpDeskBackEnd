class Package:
    def __init__(self,
                 package_id: str = None,
                 package_name: str = None,
                 duration: str = None,
                 description: str = None,
                 slot_number: str = None,
                 slot_server: str = None,
                 price: str = None,
                 status: str = None) -> None:
        self.package_id = package_id
        self.package_name = package_name
        self.duration = duration
        self.description = description
        self.slot_number = slot_number
        self.slot_server = slot_server
        self.price = price
        self.status = status