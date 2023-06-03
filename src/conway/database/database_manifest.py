import abc

class DataBaseManifest(abc.ABC):

    '''
    This is a datastructure class, used to hold identifying metadata about the "database" used by an application
    built with the conway module.

    A "database" in this domain model is represented as partitioned into one or more 
    :class:`DataHub <conway.database.data_hub.DataHub>` objects.
    '''
    def __init__(self):
        pass

    @abc.abstractmethod
    def get_data_hubs(self):
        '''
        :return: an list of :class:`DataHub <conway.database.data_hub.DataHub>` objects that comprise
        the database identified by self.

        :rtype: list
        '''
