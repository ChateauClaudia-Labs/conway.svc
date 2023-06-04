from conway.dataset.dataset_identity                       import DataSetIdentity


class StaticDataSetIdentity(DataSetIdentity):

    '''
    '''
    def __init__(self, name: str):
        super().__init__(name)