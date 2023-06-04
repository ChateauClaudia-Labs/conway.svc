
from conway.dataset.field                                  import Field
class AnyOfFilter():

    '''
    Represents an "OR" filter on a dataset, where a dataset element passes the filter if its the value of
    `field` in in the list of `allowed_values`
    '''
    def __init__(self, field: Field, allowed_values: list):
        self.field                                  = field
        self.allowed_values                         = allowed_values