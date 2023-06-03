import random

from conway.util.dataframe_utils                                   import DataFrameUtils

from conway.projector.sampler                                      import Sampler

class RandomSampler(Sampler):

    '''
    Concrete Sampler class that randomly samples a percentage of the input DataFrames.

    :param float percent: indicates the number of rows that the sampled DataFrames must contain. 
    :param int: seed  used as a seed for the random generator. Normally this is None, but for test cases
        a seed needs to be set in order to have deterministic output.
    '''
    def __init__(self, percent, seed=None):
        self.percent                                                = percent
        self.seed                                                   = seed

        super().__init__()

    def generate_sample(self, raw_data_dict):
        
        DFU                                                         = DataFrameUtils()
        sample_data_dict                                            = {}

        if not self.seed is None:
            random.seed(self.seed)
            
        # First sample the exports. Later we'll handle the sampling of the proofs, which has a dependency on the way how
        # exports are sampled, since we need proofs samples to include all the vulnerable items present in the sampled exports.
        for key in raw_data_dict.keys():
            full_df                                                 = raw_data_dict[key]
            sample_size                                             = len(full_df.index)
            sampled_index                                           = random.sample(list(full_df.index), 
                                                                                    int(self.percent * sample_size))

            sample_df                                               = full_df.filter(items=sampled_index, axis=0) 
            sample_df                                               = DFU.re_index(sample_df)
            sample_data_dict[key]                                   = sample_df

        return sample_data_dict
