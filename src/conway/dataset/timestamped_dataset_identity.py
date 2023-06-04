from conway.dataset.dataset_identity                       import DataSetIdentity
from conway.util.timestamp                                 import Timestamp


class TimestampedDataSetIdentity(DataSetIdentity):

    '''
    '''
    def __init__(self, name: str, timestamp: Timestamp):
        super().__init__(name)
        self.timestamp                                              = timestamp