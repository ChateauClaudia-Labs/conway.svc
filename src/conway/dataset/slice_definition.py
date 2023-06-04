from conway.dataset.any_of_filter                          import AnyOfFilter


class SliceDefinition():

    '''
    '''
    def __init__(self, filters_to_apply: list[AnyOfFilter]):
        self.filters_to_apply                                   = filters_to_apply