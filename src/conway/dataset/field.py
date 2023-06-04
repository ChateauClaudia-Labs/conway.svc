import abc

class Field(abc.ABC):

    '''
    '''
    def __init__(self, name: str, field_type: str):
        self.name                                   = name
        self.field_type                             = field_type

