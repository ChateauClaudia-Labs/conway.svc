from conway.dataset.timestamped_dataset_identity           import TimestampedDataSetIdentity
from conway.dataset.slice_definition                       import SliceDefinition

from conway.util.timestamp                                 import Timestamp


class SliceDataSetIdentity(TimestampedDataSetIdentity):

    '''
    '''
    def __init__(self, name: str, timestamp: Timestamp, slice_definition: SliceDefinition):
        super().__init__(name, timestamp)
        self.slice_definition                           = slice_definition