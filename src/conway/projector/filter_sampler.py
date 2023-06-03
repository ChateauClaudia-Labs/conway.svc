from conway.projector.sampler                                      import Sampler

from conway.util.dataframe_utils                                   import DataFrameUtils

class FilterSampler(Sampler):

    def __init__(self, column, matching_tag_list):
        '''
        Concrete Sampler class that samples each DataFrame input `raw_df` by filtering to rows with that meet this condition:

        * The value X of the row at column `column` must contain one of the tags in the list `matching_tag_list`

        If the parameter `column` is not really a colum in an input DataFrame, then such input DataFrame is returned as is.

        @param column A string, representing a column in input DataFrames to be used for filtering
        @param matching_tag_list An list of the tags to use for filtering rows in each input DataFrames.
        '''
        self.column                                                 = column
        self.matching_tag_list                                      = matching_tag_list

        super().__init__()

    def generate_sample(self, raw_data_dict):
        DFU                                                         = DataFrameUtils()
        sample_data_dict                                            = {}

        for key in raw_data_dict.keys():
            full_df                                                 = raw_data_dict[key]
            if self.column in full_df.columns:
                sample_df                                           = DFU.slice(full_df, self.column, self.matching_tag_list)
                sample_df                                           = DFU.re_index(sample_df)

            else:
                sample_df                                           = full_df
            sample_data_dict[key]                                   = sample_df

        return sample_data_dict
