from conway.dataset.field                                          import Field

class UnboundedField(Field):

    '''
    '''
    def __init__(self, name: str, field_type: str):
        super().__init__(name, field_type)