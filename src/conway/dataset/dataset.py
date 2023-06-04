from conway.dataset.dataset_identity                       import DataSetIdentity
from conway.dataset.dataset_content                        import DataSetContent

class DataSet():

    '''
    '''
    def __init__(self, id: DataSetIdentity, content: DataSetContent):
        self.id                                             = id
        self.content                                        = content