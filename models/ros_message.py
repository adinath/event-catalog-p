from typing import List


class Field:
    def __init__(self, name: str, datatype: str, description: str = None):
        self.name = name
        self.datatype = datatype
        self.description = description

class RosMessage:
    def __init__(self, name: str, version: str = "1.0",
                 summary: str = "",
                 description: str = "",
                 owner: str = "",
                 producers: List[str] = [],
                 consumers: List[str] = [],
                 fields: List[Field] = []):
        self.name = name
        self.version = version
        self.summary = summary
        self.description = description
        self.owner = owner
        self.producers = producers
        self.consumers = consumers
        self.fields = fields
