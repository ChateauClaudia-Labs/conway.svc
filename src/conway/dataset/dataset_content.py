import abc

from conway.dataset.slice_definition                             import SliceDefinition



class DataSetContent(abc.ABC):
    '''
    '''
    def __init__(self):
        pass

    @abc.abstractmethod
    def filter(self, slice_def: SliceDefinition):
        '''
        :param SliceDefinition slice_def:
        :return: A subset of `self`, consisting of the elements in `self` that comply with the `slice_def`
        :rtype: DataSetContent
        '''
