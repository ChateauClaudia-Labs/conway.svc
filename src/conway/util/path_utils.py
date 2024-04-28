import os                                                   as _os

from pathlib                                                import Path
import shutil           

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

        :param str path: path that is to be clearned up.
        '''
        modified_path                           = path.replace("\v", "/v")          \
                                                    .replace("\\", "/")         \
                                                    .replace("//", "/")
        return modified_path
    

    def to_linux(self, path, absolute=True):
        '''
        Takes a path that might be a Windows or Linux path, and returns a linux path

        :param str path: Initial path to clean up
        :param bool absolute: Optional parameter that is True by default. If True, then the `path` is first expanded to an
                        absolute path, and the linux equivalent is returned. Otherwise, the `path` is treated as a
                        relative path and a linux equivalent relative path is returned.
        :returns: a Linux equivalent for the `path` parameter
        :rtype: str
        '''
        if absolute:
            path                                = _os.path.abspath(path)
        # The following line does not change the input if we are Linux, but will if we are Windows
        linux_path                              = path.replace("\\", "/")
        return linux_path
    
    def remove(self, path):
        '''
        Removes all contents under the absolute path ``path``. If the path does not exist, it just returns without triggering
        error messages.

        :param str path:
        '''
        if Path(path).exists():
            shutil.rmtree(path)

