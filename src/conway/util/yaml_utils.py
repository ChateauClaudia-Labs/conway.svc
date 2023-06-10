import yaml                                         as _yaml

class YAML_Utils():
    '''
    Utility class consisting of helper methods to manipulate YAML files.
    '''
    def __init__(self):
        pass

    def load(self, path):
        '''
        :param str path: The location of the YAML file to be loaded
        :return: the contents of the YAML file
        :rtype: dict
        '''
        try:
            with open(path, "r", encoding="utf8") as file:
                loaded_dict                             = _yaml.load(file, Loader=_yaml.FullLoader)
                return loaded_dict
        except Exception as ex:
            raise ValueError("Unable to load YAML file '" + str(path) + "'. Error is:\n\t" + str(ex))