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

        It encapsulate the current Excel or CSV-based implementation and provides encpasulation for potential future
        performance improvements.
        '''
        self.url                            = url
        self.subpath                        = subpath

        self.optimize                       = None # This is set in the __enter__ method
        self.ACTION                         = None # Must be populated by specific methods; used to provide context in error messages

    def __enter__(self, optimize=False):
        '''
        Returns self after initializing internal state

        :param bool optimize: if True, then will attempt to retrieve a CSV version of self.url instead of an Excel file, if
            such a CSV exists.
        '''
        self.optimize                       = optimize

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
        Creates and returns a DataFrame by loading an CSV or Excel spreadsheet, removing any spurious columns if needed.

        As a performance optimization, it will attempt to load from a CSV file, if one exists that corresponds
        to ``self.url``, even if ``self.url`` might reference an Excel spreadshet.

        For example, if ``self.url`` is ``C:/foo/bar/dataset.xlsx``, this method will change the filename
        to a CSV filename ``C:/foo/bar/dataset.csv``, and if such a CSV file exists, it will load and return it.

        If the CSV file does not exist, it will try to load an Excel file from ``self.url``. When attemptoing
        to load from an Excel format then this method has logic to look for the worksheet called ``self.subpath``
        (or, if ``self.subpath`` is None, for a worksheet called "Sheet1").
        If no such worksheet exists, then this method fails over to look for worksheets in ``alternative_subpaths``, until
        one is found. If not is found then this method returns None, unless fail_if_not_found`` is True, 
        in which case it raises a ValueError.

        :param list alternative_subpaths: A list of strings. It's optional and is empty by default. Used in cases
            when the dataset is not found at self.url[self.subpath] - if so, a re-try is made successively
            with each member of `alternative_subpaths` in lieus of self.subpath. The dataset retrieved from the
            first success is returned. If not is found, the method returns None

        :param bool fail_if_not_found: when True then method raises a :class:`ValueError` if dataset is not found. Else
            method returns ``None`` when dataset is not found.
        '''

        self.ACTION                         = "retrieve"

        result_df                           = self._retrieve_csv(fail_if_not_found=False)
        if not result_df is None:
            return result_df
        else: # Backup legacy case: try to load as an Excel file
            result_df                       = self._retrieve_excel(alternative_subpaths, fail_if_not_found)
        
        sheet_name                          = self.subpath
        if sheet_name is None:
            sheet_name                      = "Sheet1"
        sheets_to_try                       = [sheet_name] + alternative_subpaths

        if result_df is None and fail_if_not_found:
            raise ValueError("Dataset " + str(self.url) + " either does not exist or if it does then it doesn't any "
                             + " worksheet called '" + "', '".join(sheets_to_try) + "'")

        return result_df
    
    def _url_to_csv(self, some_url):
        '''
        Given a filename for a dataset, it returns the CSV-equivalent filename.

        For example, if ``some_url`` is ``C:/foo/bar/dataset.xlsx" or ``C:/foo/bar/dataset, 
        this method returns ``C:/foo/bar/dataset.csv".

        It gets more nuanced than that if the original ``some_url`` is an Excel filename that is supposed to have
        multiple "sheets". In that case there might be multiple CSV equivalents, one per sheet.

        For example, if ``some_url`` is ``C:/foo/bar/dataset.xlsx" and logically it should have multiple

        :param str some_url: Identifies an Excel or CSV file representing a dataset.
        '''
        if some_url.endswith(".xlsx"):
            result                          = some_url[:-4] + ".csv"
        elif some_url.endswith(".csv"):
            result                          = some_url
        else:
            result                          = some_url + ".csv"
        return result


    def _retrieve_csv(self, fail_if_not_found=False):
        '''

        '''
        DFU                                 = DataFrameUtils()
        csv_path                            = self._url_to_csv(self.url)
        if not Path(csv_path).exists():
            if fail_if_not_found:
                raise ValueError("Dataset '" + str(csv_path) + "' does not exist")
            else:
                return None
        
        result_df                           = None
        
        try:
            result_df                       = DFU.load_csv(csv_path)
        except Exception as ex:
            if fail_if_not_found:
                raise ValueError(f"Unable to retreive {csv_path} because of this error: '{ex}'")
            else:
                result_df                   = None

        return result_df    

    def _retrieve_excel(self, alternative_subpaths=[], fail_if_not_found=False):

        '''

        '''
        DFU                                 = DataFrameUtils()
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
        Path(src_url).mkdir(parents=True, exist_ok=True)
        _shutil.copytree(src                = src_url, 
                         dst                = self.url,
                         dirs_exist_ok      = True)