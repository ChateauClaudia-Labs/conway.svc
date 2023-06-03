from pathlib                                                        import Path
import os                                                           as _os
import pandas                                                       as _pd
import shutil                                                       as _shutil

from conway.util.dataframe_utils                       import DataFrameUtils

class DataAccessor():

    def __init__(self, url, subpath=None):
        '''
        Context manager to provide safe functionality to load datasets for the `vulnerability_management`
        module.

        It encapsulate the current Excel-based implementation and provides encpasultion for potential future
        performance improvements.
        '''
        self.url                            = url
        self.subpath                        = subpath

        self.ACTION                         = None # Must be populated by specific methods; used to provide context in error messages

    def __enter__(self):
        '''
        Returns self after initializing internal state
        '''
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        '''
        Frees resources.
        '''

        if isinstance(exc_value, PermissionError):
            raise ValueError("Please close file(s) under " + self.url + " so system can " + self.ACTION + " it. Thanks.")
        elif isinstance(exc_value, Exception):
            raise exc_value
        
        suffix                              = ""
        if not self.subpath is None:
            suffix                          = " [" + self.subpath + "]"
        #print(self.ACTION + " '" + self.url + suffix + "': DONE")

        ''' TODO - figure out if we want to handle some types of exceptions
        if isinstance(exc_value, IndeExError):
            # Handle IndexError here...
            print(f"An exception occurred in your with block: {exc_type}")
            print(f"Exception message: {exc_value}")
            return True
        '''

    def retrieve(self, alternative_subpaths=[], fail_if_not_found=False):
        '''
        Creates and returns a DataFrame by loading an Excel spreadsheet, removing any spurious columns if needed.
        If there no such file exists, or if it exists but has no worksheet called `self.subpath` or
        in `alternative_subpaths`, then it return None, unless fail_if_not_found`` is True, in which case
        it raises a ValueError.

        :param list alternative_subpaths: A list of strings. It's optional and is empty by default. Used in cases
            when the dataset is not found at self.url[self.subpath] - if so, a re-try is made successively
            with each member of `alternative_subpaths` in lieus of self.subpath. The dataset retrieved from the
            first success is returned. If not is found, the method returns None

        :param bool fail_if_not_found: when True then method raises a :class:`ValueError` if dataset is not found. Else
            method returns ``None`` when dataset is not found.
        '''
        DFU                                 = DataFrameUtils()
        self.ACTION                         = "retrieve"
        if not Path(self.url).exists():
            if fail_if_not_found:
                raise ValueError("Dataset '" + str(self.url) + "' does not exist")
            else:
                return None
        
        sheet_name                          = self.subpath
        if sheet_name is None:
            sheet_name                      = "Sheet1"
        sheets_to_try                       = [sheet_name] + alternative_subpaths
        result_df                           = None
        for sheet in sheets_to_try:
            try:
                result_df                   = DFU.load_excel(self.url, sheet_name=sheet)
            except ValueError as ex:
                if str(ex) == "Worksheet named '" + sheet + "' not found":
                    continue # Try next sheet
                else:
                    raise ex
            # If we get here then we succeeded
            break

        if result_df is None and fail_if_not_found:
            raise ValueError("Dataset " + str(self.url) + " either does not exist or if it does then it doesn't any "
                             + " worksheet called '" + "', '".join(sheets_to_try) + "'")

        return result_df
    
    def persist(self, data_df: _pd.DataFrame):
        '''
        '''
        sheet_name                          = self.subpath
        if sheet_name is None:
            sheet_name                      = "Sheet1"
        folder                              = _os.path.dirname(self.url)
        Path(folder).mkdir(parents=True, exist_ok=True)
        data_df.to_excel(self.url, sheet_name=sheet_name)

    
    def remove(self):
        '''
        '''
        self.ACTION                         = "remove"
        if Path(self.url).exists():
            _shutil.rmtree(self.url)

    def copy_from(self, src_url):
        '''
        '''
        self.ACTION                         = "copy"
        _shutil.copytree(src                = src_url, 
                         dst                = self.url,
                         dirs_exist_ok      = True)