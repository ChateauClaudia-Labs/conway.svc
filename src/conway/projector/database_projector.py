import abc
from pathlib                                                            import Path
import pandas                                                           as _pd

from conway.application.application                        import Application
from conway.observability.logger                           import Logger

from conway.database.database_manifest                     import DataBaseManifest
from conway.database.data_accessor                         import DataAccessor

from conway.dataset.dataframe_dataset_content              import DataFrameDataSetContent
from conway.dataset.dataset_identity                       import DataSetIdentity
from conway.dataset.slice_definition                       import SliceDefinition


class DataBaseProjector(abc.ABC):

    '''
    :param int target_size: Number of Vulnerable item identifiers to which the projection must attempt to restrict itself

    :param list brands_l: If not null, will cause the import datasets to be filtered to only these brands first
    '''
    def __init__(self, datasets_in_scope: list[DataSetIdentity], target_size: int):
        self.datasets_in_scope                              = datasets_in_scope
        self.target_size                                    = target_size

        # This will be set when self.project(-) runs
        self.source_data_dict                               = None


    @abc.abstractmethod
    def projection_filter(self) -> SliceDefinition:
        '''
        :returns: The object that knows how to filter datasets in an input database to get projected datasets
        '''

    def must_save_even_if_empty(self, relative_url) -> bool:
        '''
        Consultative method which concrete classes may overwrite.

        By default, the projector will not save project datasets if they are empty. However, concrete
        classes may decide that some datasets must always exist, even if empty. If so, concrete classes
        can use this method as an "escape hatch" in the projector logic.

        :param str relative_url: The path under an Application's data hub for a dataset that is being
            considered to be saved by the projeector.
        :return: True if the projected dataset identified by the ``relative_url`` parameter must be saved
            by the ``self.project`` method, even if the dataset ise empty. False otherwise. False is the
            default
        :rtype: bool
        '''
        return False

    def project(self, input_db: 	DataBaseManifest, output_db: DataBaseManifest) -> _pd.DataFrame:
        '''
        :return: A DataFrame with a row for each dataset that was processed, listing this information:
            * relative path for input and output
            * number of rows, columns for input and output


        '''
        # These lists will be built along the way, one element per dataset processed, and used in the end
        # to create the returned DataFrame
        #
        stats_input_relative_paths                          = []
        stats_input_nb_rows                                 = []
        stats_input_nb_columns                              = []

        stats_output_relative_paths                         = []
        stats_output_nb_rows                                = []
        stats_output_nb_columns                             = []


        # ------------------- Step 1: load everything ---------------------
        nb_loaded                                           = 0
        nb_in_scope                                         = len(self.datasets_in_scope)

        # Keys will be dataset URLs, and values will be _DataSetInfo objects. One entry for each dataset
        # we process (i.e., one entry per each member of self.datasets_in_scope)
        #
        self.source_data_dict                               = {}

        # Dictionary, one entry per hub. Keys are names of hubs, values are sets of the relative_urls for datasets
        # skipped by that hub. Used to later get the intersection of what was skipped by all hubs: these are datasets
        # that are potentially a problem, since the user specification made it sound like they should be there, so
        # we want to track that.
        skipped_datasets                                    = {}
        all_dataset_rel_urls_s                              = set()
        for hub in input_db.get_data_hubs():    
            skipped_by_hub                                  = set()
            Application.app().log(message                   = "---------- Working in DataHub " + str(hub.name) + " ----------", 
                                    log_level               = Logger.LEVEL_INFO)

            for dataset_id in self.datasets_in_scope:
                relative_url                                = dataset_id.path_within_hub()
                all_dataset_rel_urls_s.add(relative_url)
                subpath_l                                   = dataset_id.subpaths()
                full_url                                    = hub.hub_root() + "/" + relative_url
                    

                if not Path(full_url).exists():
                    skipped_by_hub.add(relative_url)
                    continue # Skip this dataset; can't project something that does not exist in this hub

                Application.app().log(message               = "\t\tloading '" + str(relative_url) + "'", 
                                    log_level               = Logger.LEVEL_INFO)


                # If the dataset we are loading is split across multiple subpaths (e.g., multiple worksheets in a single
                # Excel file, say), we need to detect that, load the different pieces and concatenate them together
                # 
                df_list                                     = []
                for subpath in subpath_l:
                    sub_df                                  = DataAccessor(url=full_url, subpath=subpath).retrieve()
                    if not sub_df is None:
                        df_list.append(sub_df)
                data_df                                     = _pd.concat(df_list    )
                self.source_data_dict[relative_url]         = _DataSetInfo(hub_name         = hub.name,
                                                                           hub_handle       = hub.hub_handle,
                                                                           sheet            = subpath_l[0],
                                                                           data_df          = data_df)
                stats_input_relative_paths.append(relative_url)
                stats_input_nb_rows.append(len(data_df.index))
                stats_input_nb_columns.append(len(data_df.columns))

                nb_loaded                                   += 1
                Application.app().log(  message             = "data_df.shape=" + str(data_df.shape) + " *** Loaded '" + str(relative_url) + "'", 
                                        log_level           = Logger.LEVEL_DEBUG)
            # Before we start looking inside the next hub, remember what his hubs skipped
            skipped_datasets[hub.name]                      = skipped_by_hub
        
        # If we didn't process everything, list it here:
        if nb_loaded < nb_in_scope:
            skipped_by_all_hubs_s                           = all_dataset_rel_urls_s # Start big and make the set smaller by intersection
            for hub_name in skipped_datasets.keys():
                skipped_by_hub                              = skipped_datasets[hub_name]
                skipped_by_all_hubs_s                       = skipped_by_all_hubs_s.intersection(skipped_by_hub)

            skipped_msg                                     = "\n\tSkipped: " + "\n\t\t".join(skipped_by_all_hubs_s)
        else:
            skipped_msg                                     = ""
        Application.app().log(  message                     = "---------- Loaded " \
                                                                + str(nb_loaded) + "/ " + str(nb_in_scope) \
                                                                + " datasets ----------"
                                                                + skipped_msg,
                                log_level                   = Logger.LEVEL_INFO)


        
        # ------------------- Step 2: Build the projected data sets ---------------------
        #
        #
        nb_projected                                            = 0
        projected_data_dict                                     = {}
        for projected_hub in output_db.get_data_hubs():

            for relative_url in self.source_data_dict.keys():
                data_info                                       = self.source_data_dict[relative_url]
                if projected_hub.name != data_info.hub_name:
                    # This dataset is not for this hub, we will process it later when we loop through the hub 
                    # that this dataset belongs to
                    continue

                projection_filter                               = self.projection_filter()
                data_df                                         = data_info.data_df

                data_content                                    = DataFrameDataSetContent(data_df)

                projected_content                               = data_content.filter(projection_filter)
                projected_df                                    = projected_content.data_df

                projected_info                                  = _DataSetInfo(hub_name             = projected_hub.name,
                                                                               hub_handle           = projected_hub.hub_handle,
                                                                               sheet                = data_info.sheet,
                                                                               data_df              = projected_df)
                projected_data_dict[relative_url]               = projected_info

                stats_output_relative_paths.append(relative_url)
                stats_output_nb_rows.append(len(projected_df.index))
                stats_output_nb_columns.append(len(projected_df.columns))

                nb_projected                                    += 1
                Application.app().log(  message             = "data_df.shape: " + str(data_df.shape) + "->" + str(projected_df.shape)\
                                                                + " *** Projected '" + str(relative_url) + "'", 
                                        log_level           = Logger.LEVEL_DEBUG)


        Application.app().log(  message                         = "---------- Projected " \
                                                                    + str(nb_projected) + "/ " + str(nb_in_scope) \
                                                                    + " datasets ----------", 
                                log_level                       = Logger.LEVEL_INFO)


        # ------------------ Step 3: save the projections ----------------------------
        #
        nb_saved                                                = 0
        for relative_url in projected_data_dict.keys():
            projected_info                                      = projected_data_dict[relative_url]
            projected_df                                        = projected_info.data_df
            full_url                                            = projected_info.hub_handle.hub_root() + "/" + relative_url

            subpath                                             = projected_info.sheet

            # Only persiste non-empty datasets (projecting might create some empty ones, so this actually happens)
            if len(projected_df) == 0 and not self.must_save_even_if_empty(relative_url):
                continue

            DataAccessor(url=full_url, subpath=subpath).persist(data_df=projected_df)
            nb_saved                                            += 1

        Application.app().log(  message                         = "---------- Saved " \
                                                                    + str(nb_saved) + "/ " + str(nb_in_scope) \
                                                                    + " datasets ----------", 
                                log_level                       = Logger.LEVEL_INFO)
        
        # Input and output relative paths should be identical, or otherwise the stats DataFrame wouldn't line up 
        #
        assert stats_input_relative_paths == stats_output_relative_paths
        stats_df                                                = _pd.DataFrame({
                                                                        "Relative url":       stats_input_relative_paths,
                                                                        "Input nb rows":            stats_input_nb_rows,
                                                                        "Input nb columns":         stats_input_nb_columns,
                                                                        "Output nb rows":           stats_output_nb_rows,
                                                                        "Output nb columns":        stats_output_nb_columns})
        return stats_df


class _DataSetInfo():

    '''
    Helper class used as a data structure to group together some properties of DataSets as the projector
    encounters them, to be able to easily associate a projecte dataset to the origina dataset it came from
    '''
    def __init__(self, hub_name, hub_handle, sheet, data_df):
        self.hub_name                                       = hub_name
        self.hub_handle                                     = hub_handle
        self.sheet                                          = sheet
        self.data_df                                        = data_df