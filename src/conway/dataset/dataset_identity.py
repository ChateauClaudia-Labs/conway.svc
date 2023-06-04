import abc

class DataSetIdentity(abc.ABC):

    '''
    '''
    def __init__(self, name: str):
        self.name                                           = name
    
    @abc.abstractmethod
    def path_within_hub(self) -> str:
        '''
        :return: A string that gives the unique location for the dataset determined by this DataSetIdentity
            relative to the DataHub in which it resides.
        '''

    @abc.abstractmethod
    def subpaths(self) -> list[str]:
        '''
        :return: A list strings corresponding to a subpaths below ``path_within_hub`` that, in the aggregate, correspond to this
                DataSetIdentity. For example, in the context of datasets stored in Excel, this is the list of worksheets
                across which the dataset's content is stored (usually 1, but for imported data it might be split across
                multiple worksheets if the upstream system exports in batches, one batch per worksheet).
        '''