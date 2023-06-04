import abc
from pathlib                                                                    import Path

from conway.util.dataframe_utils                                   import DataFrameUtils

class Sampler(abc.ABC):

    def __init__(selfS):
        '''
        Root class for hierarchy of algorithms that can sample large datasets into smaller datasets suitable for
        usage in test cases. The intention is to support the development of test cases that don't run too long just
        because the inputs are unnecessarily large.

        Thus, sampling algorithms are expected to maintain enough variation/richness in the datasets they generate
        so that test cases remain meaningful and exercise nuances in the business logic. But within that constraint,
        be as minimalist as practical.

        '''
        pass

    @abc.abstractmethod
    def generate_sample(self, raw_data_dict):
        '''
        Returns a dictionary where the keys are strings and the values are DataFrames. 

        The keys match must be a subset of the keys in the `raw_data_dict` parameter. Normal usage is for keys
        to be filenames (e.g., "230228 sn_vul_detection since Jan 1.xlsx").

        For each key, the value in the returned dictionary is a DataFrame that is a "sample" of the corresponding
        DataFrame in the `raw_data_dict` parameter.

        For example, consider an example with this notation:
         
            * Define      K                   ="230228 sn_vul_detection since Jan 1.xlsx"
            * Assume      K is a key in `self.raw_data_dict`
            * Define      `sample_data_dict`  to be the returned value of this method
            * Define      `raw_K_df           = self.raw_data_dict[K`]
            * Define      `sample_K_df        = sample_data_dict[K`]

        Then this method guarantees the following:

            * `sample_K_df` is either missing or is a DataFrame. Each concrete class's functional spec determines if it is 
                OK for it to be missing (for example, if `raw_sample_K_df` is only an input to the sampling, but doesn't
                need to be sampled itself.).
            * If not null, `sample_K_df` has exactly the same columns as `raw_K_df` and a subset of its rows.
            * The row index of `sample_K_df` is a range 0,1,2,.. so it does not match the row index of `raw_K_df`

        @param raw_data_dict A dictionary, where the keys are strings identifying a kind of dataset, and the values
            are DataFrames that must be sampled. Normal usage is for keys to be filenames 
            (e.g., "230228 sn_vul_detection since Jan 1.xlsx").

        '''

    def value_list(self, raw_data_dict, column):
        '''
        Helper method to assist some callers of concrete classes.

        It returns a list, consisting of all the possible values (without duplicates) for column `column` across
        all DataFrames in the `raw_data_dict`

        @param raw_data_dict A dictionary, where the keys are strings identifying a kind of dataset, and the values
            are DataFrames intended to be sampled. Normal usage is for keys to be filenames 
            (e.g., "230228 sn_vul_detection since Jan 1.xlsx").
        @param column A string, representing a column in input DataFrames to be used for filtering

        '''
        DFU                                                         = DataFrameUtils()

        sample_data_dict                                            = {}
        values_s                                                    = set()
        for key in raw_data_dict.keys():
            full_df                                                 = raw_data_dict[key]
            if column in full_df.columns:
                values_s                                            = values_s.union(set(full_df[column].unique()))

        values_list                                                 = list(values_s)
        return values_list
    
    def create_samples(self, raw_data_dict, path, worksheet=None):
        '''
        Generates samples from `raw_data_dict` by calling self.generate_sample(-), and then saves all the generated
        DataFrames to the given path, using the same filename as the original DataFrame from which they were sampled, 
        i.e., using as a filename the key in `raw_data_dict`. 

        It also returns the dictionary of sampled DataFrames that it saves.

        @param raw_data_dict A dictionary whose keys are filenames and the values are DataFrames of to be sampled.

        @param path A string, corresponding to the path under which to save the Excel filename containing the DataFrame content.
        @param worksheet A string, corresponding to the worksheet in the Excel spreadsheet under which to save the DataFrames' content.
            If it is None then the worksheet used will be "Sheet1"
        '''
        sampled_df_dict                                             = self.generate_sample(raw_data_dict)
        Path(path).mkdir(parents=True, exist_ok=True) # Making sure path exists, and creating it if it does not
        if worksheet is None:
            worksheet                                               = "Sheet1"
        for filename in sampled_df_dict.keys():
            sample_df                                               = sampled_df_dict[filename] 
            sample_df.to_excel(path + "/" + filename, sheet_name=worksheet) 
        return sampled_df_dict 

