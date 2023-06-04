

class PathUtils():

    def __init__(self):
        '''
        '''

    def clean_path(self, path):
        '''
        Replaces characters in `path` that have a special meaning in Windows by other characters that will give the intended
        behaviour in Linux.

        In particular:

            * "\v" in Windows is interpreted as "\x0b", so to prevent this we replace "\v" by "/v"
            * "\" in Windows is interpreted as a folder separator, so we replace it by "/"
            * In the above replacements, an additional "\" is needed as an escape character

        Then returns the modified path
        '''
        modified_path                   = path.replace("\v", "/v")          \
                                                .replace("\\", "/")         \
                                                .replace("//", "/")
        return modified_path