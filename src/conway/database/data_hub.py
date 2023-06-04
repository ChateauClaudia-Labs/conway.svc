import abc

class DataHub(abc.ABC):

    '''
    This is a datastructure class, used to hold the specification for a portion of the database associated
    to an application built with the conway module.

    The conway is geared towards the development of pipeline applications that provide services
    to transform certain Excel spreadsheets into other Excel spreadshets, typically across multiple 
    "data science" steps involving data analysis and enrichment.

    The "database" for such an application is a collection of folder structure in the (possibly remote)
    file system in which those Excel spreadsheets reside.

    The Excel spreadsheets are organized into taxonomies, and each such taxonomy is what we call a "Data Hub".

    For example, there might be an "input hub" and a "publication hub".
    Typically in those situations, the system is fed Excel spreadsheets from upstream systems, and these go into the
    "input hub". The system then does its data processing, and deposits the resulting Excel spreadsheets in the
    "publication hub".

    :param str name: Uniquely identifies this DataHub among all other DataHubs of the database.
    '''
    def __init__(self, name: str):
        self.name                           = name

    @abc.abstractmethod
    def populate_from_seed(self, seed_hub):
        '''
        @param seed_hub A SingleRootDataHub object. This method will wipe out any pre-existing contents of self and
                initialize it to be a copy of what is inside the `seed_hub`
        '''

    @abc.abstractmethod    
    def enrich_from_seed(self, seed_hub):
        '''
        @param seed_hub A SingleRootDataHub object. This method will enrich the contents of self by adding
            additional content from the `seed_hub`. If the new content has the same filename as pre-existing
            content, then the pre-existing content is overwritten.
        '''


    @abc.abstractmethod
    def create_snapshot(self, snapshot_root_folder):
        '''
        This method creates a copy of this DataHub content and saves it to a folder whose name is given by the
        `snapshot_name` parameter. 

        A main use case for this notion of "snapshot" is the test harness: some tests need to exercise the business
        logic over multiple time periods, and in the process may want to save a copy of what a DataHub's content
        is at various points along the way. 

        Here is an example for such a use case, identified as scenario 1001. Suppose this method is called on an 
        DataHub object representing content under a root like

            ".../vulnerability_management_scenarios/1001/ACTUALS@latest/publications"

        In our use case, the test case might want to do multiple snapshots that can be thought of as "ACTUALS@T1", "ACTUALS@T2", 
        "ACTUALS@T3", etc. for what the database looked at various points in the test's dataflow, such as at times T1, T2, T3, ... 

        The parameter `snapshot_root_folder` should be given in accordance with that intention. For example, if the intention
        is to snapshot data as of time T2, the natural value for the `snapshot_root_folder` parameter would be 

            ".../vulnerability_management_scenarios/1001/ACTUALS@T2/publications"


        @param snapshot_root_folder A string that identifies the full path to the snapshot
        '''
