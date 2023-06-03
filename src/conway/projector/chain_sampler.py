from conway.projector.sampler                                      import Sampler

class ChainSampler(Sampler):

    def __init__(self, sampler_list):
        '''
        Concrete Sampler class that composes a list of samplers: each sampler is called in succession
        feeding its output as the input of the next sampler
        '''
        super().__init__()
        
        self.sampler_list                                           = sampler_list

    def generate_sample(self, raw_data_dict):

        data_dict                                                   = raw_data_dict

        if len(self.sampler_list) == 0:
            raise ValueError("ChainSampler can't run because the list of Samplers to be chained is an empty list")
        
        for sampler in self.sampler_list:
            data_dict                                               = sampler.generate_sample(data_dict)

        return data_dict
