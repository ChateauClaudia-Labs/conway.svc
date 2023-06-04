from conway.projector.sampler                                      import Sampler

class FirstFoundSampler(Sampler):

    def __init__(self, sample_size):
        '''
        Concrete Sampler class that samples each DataFrame input by taking the first `sample_size`-many rows.

        @param sample_size An int, indicating the number of rows that the sampled DataFrames must contain. 
        '''
        self.sample_size                                            = sample_size

        super().__init__()

    def generate_sample(self, raw_data_dict):

        sample_data_dict                                            = {}

        # First sample the exports. Later we'll handle the sampling of the proofs, which has a dependency on the way how
        # exports are sampled, since we need proofs samples to include all the vulnerable items present in the sampled exports.
        for key in raw_data_dict.keys():
            full_df                                                 = raw_data_dict[key]
            sample_df                                               = full_df[:self.sample_size]  
            sample_data_dict[key]                                   = sample_df

        return sample_data_dict
