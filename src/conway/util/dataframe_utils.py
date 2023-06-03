import pandas                                                           as _pd
import datetime                                                         as _datetime
import math
import numbers

from conway.util.timestamp                                 import Timestamp                

class DataFrameUtils():

    def __init__(self):
        '''
        This class provides some utilities for manipulating DataFrame information and produce more user-friendly
        derived DataFrames
        '''
        pass

    BLANK_VALUE                                 = "-"
    

    def fill_nan(self, df, columns, fill_value=BLANK_VALUE):
        '''
        Returns a new DataFrame obtained from df by filling out any "NaN" in any of the columns in 'columns'
        by the string `fill_value`. By default it is "-"

        @param fill_value A string. If not set, it is assumed to be "-". Used to fill nans.
        '''
        df0                                 = df
        for col in columns:
            df0                             = df0.fillna(value={col: fill_value})
        return df0
    
    def clean_numeric_columns(self, df, columns, fill_value=0):
        '''
        Returns a new DataFrame obtained from `df` by replacing any non-numeric value in any of the columns in
        `columns` with `fill_value`

        @param fill_value A float or int. If not set, it is assumed to be 0.
        '''
        def _make_numeric(row, col):
            val                             = row[col]
            if isinstance(val, numbers.Number):
                return val
            else:
                return fill_value
            
        df0                                 = df.copy()
        for col in columns:
            df0[col]                        = df0.apply(lambda row: _make_numeric(row, col), axis=1)
        return df0
    
    def clean_boolean_columns(self, df, columns, only_booleans=False):
        '''
        Returns a new DataFrame obtained from `df` by replacing any 0 or 1 in the columns in
        `columns` with False or True, respectively

        :param pandas.DataFrame df: dataset to clean up
        :param list columns: boolean-valued columns in ``df`` that must be cleaned up
        :param bool only_booleans: If True, this method will raise a ValueError if any row has a non-boolean value
            in the any of the given columns.
        '''
        def _restore_boolean_types(row, col):
            '''
            Used to correct data "corruption" when Pandas loads an Excel with a column of True's, False's and blanks.
            Pandas seems to convert the True/False to 1/0, so this function is to restore the boolean types.
            '''
            val                             = row[col]
            if val == 1:
                return True
            elif val ==0:
                return False
            else:
                return val
        # It is tricky to check for non-boolan, since DataFrame comparators like "df0[boolean_column]==True" will return 
        # true if value is 1, which we consider "spurious". So to pick up the spurious, we convert values
        # to a string since then "1" and "True" will not match
        def _is_spurious(row, boolean_column):
            val                                                 = row[boolean_column]
            if str(val) != "True" and str(val) != "False":
                return True
            else:
                return False

            
        df0                                 = df.copy()
        for col in columns:
            if col in df0.columns:
                df0[col]                    = df0.apply(lambda row: _restore_boolean_types(row, col), axis=1)

                if only_booleans == True:
                    bad_df                  = df0[df0.apply(lambda row: _is_spurious(row, col), axis=1)]
                    if len(bad_df) > 0:
                        bad_vals            = [str(x) for x in bad_df[col].unique()]
                        raise ValueError("Non-booleans found in column '" + str(col) + "': '" + "', '".join(bad_vals) + "'")
                
        return df0
 

    def clean_date_columns(self, input_df, date_columns):
        '''
        Creates and returns a DataFrame that has the same columns and rows as `input_df`, except that any column
        in parameter `date_columns` is "cleaned up", i.e. converted to a string in the format
        "YY-MM-DD" if it is a pandas._libs.tslibs.timestamps.Timestamp

        @param input_df A DataFrame, whose date columns we want to clean up
        @param date_columns A list of strings, corresponding to those columns in `input_df` that contain date content.
        '''
        def _clean_date(dirty_date):
            '''
            Helper method
            '''
            if type(dirty_date)==_pd._libs.tslibs.timestamps.Timestamp:
                clean_date                                          = dirty_date.date().strftime("%y-%m-%d")
            elif type(dirty_date)==_datetime.datetime:
                clean_date                                          = dirty_date.strftime("%y-%m-%d")
            elif type(dirty_date) == int:
                ts                                                  = Timestamp.from_excel_int(dirty_date)
                clean_date                                          = ts.to_excel_date()
            else:
                clean_date = dirty_date
            return clean_date
        
        output_df                                                   = input_df.copy()
        
        for col in date_columns:
            if col in output_df.columns:
                output_df[col]                                      = output_df.apply(lambda row: _clean_date(dirty_date=row[col]), axis=1)

        return output_df

    def is_blank(self, val):
        '''
        Returns a boolean. True if `val` is either nan or an empty string
        '''
        if self.is_nan(val):
            return True
        elif type(val)==str and len(val.strip())==0:
            return True
        else:
            return False
        
    def is_nan(self, val):
        '''
        Returns a boolean. True if `val` is a float that is nan, and False otherwise.
        '''
        if isinstance(val, float) and math.isnan(val):
            return True
        elif type(val)==type(_pd.NaT):
            return True
        else:
            return False

        
    def fill_with_last_value(self, input_df, column_list):
        '''
        Returns a DataFrame that is a "copy" of `input_df`, except that we fill blanks in any column in `column_list`
        by making it equal to the last known value of that column, if any.

        @param input_df A DataFrame
        @param column_list A list of strings, corresponding to columns in `input_df`
        '''
        last_values_dict                                            = {} # Keys are columns, values are last non-blank value
        new_columns_dict                                            = {} # Keys are columns, values are lists (values of the column)

        # Reduce the columns of interest to only those that actually appear in input_df
        columns_to_fill                                             = [col for col in column_list if col in input_df.columns]
        for col in columns_to_fill:
            last_values_dict[col]                                   = None
            new_columns_dict[col]                                   = []
            
        def _has_last_value(col):
            last_val                                                = last_values_dict[col]
            if last_val is None:
                return False
            else: 
                return True
        def _last_value(col):
            last_val                                                = last_values_dict[col]
            return last_val
            
    
        for row in input_df.iterrows():
            row_nb                                                  = row[0]
            row_data                                                = row[1]
            for col in columns_to_fill:
                original_val                                        = row_data[col]
                if self.is_blank(original_val) and _has_last_value(col):
                    new_columns_dict[col].append(_last_value(col))
                else:
                    new_columns_dict[col].append(original_val)
                # In case we entered a non blank row, update the last value dict
                if not self.is_blank(original_val):
                    last_values_dict[col]                           = original_val


        # Now create the output with modified columns
        output_df                                                   = input_df.copy()
        for col in columns_to_fill:
            output_df[col]                                          = new_columns_dict[col]

        return output_df



    def slice(self, df, column, matching_tag_list):
        '''
        Returns a DataFrame obtained by filtering rows of `df` using this criterion:

        * Include a row if the value X at the row's column `column` contains at least one of the tags in the list `matching_tag_list`

        @param df A DataFrame

        @param matching_tag_list A list of possible tags to filter column `column` in DataFrame `df`
        '''
        def _is_a_match(row):
            val                                                     = row[column]
            matches                                                 = [elt for elt in matching_tag_list if type(val)==str and str(elt) in val]
            if len(matches) > 0:
                return True
            else:
                return False
        
        # GOTCHA
        #   Special case: if df is "empty" (i.e., has no rows) then the logic below doesn't work. Just return
        #   df in that case
        if len(df.index) == 0:
            return df
        
        result_df                                                   = df[df.apply(_is_a_match, axis=1)]
        return result_df
    
    def concat(self, df_list: list) -> _pd.DataFrame:
        '''
        Method for savely concatenating DataFrames, avoiding common pitfalls when the DataFrame.concat method is
        called directly

        :param list df_list:
        :returns: A :class:`DataFrame <pandas.DataFrame>` obtained by concatenating the DataFrames in ``df_list``.
            If the list is empty or only has empty DataFrames, then this method returns ``None``.
        :rtype: :class:`DataFrame <pandas.DataFrame>`
        '''
        if df_list is None:
            return None
        
        non_empty_dfs_list                  = [df for df in df_list if len(df.index)>0]
        if len(non_empty_dfs_list) == 0:
            return None
        
        result_df                           = _pd.concat(non_empty_dfs_list)
        return result_df
    
    def replace_value(self, input_df, column, old_val_list, new_val):
        '''
        Helper method to clean up user entries that do not conform to the standard, even if to a human eye they
        are close.

        For example, this method can be used to replace user-entered "Yes" in a boolean-valued column to True.
        '''
        def _replace(row):
            old_val                         = row[column]
            if old_val in old_val_list:
                return new_val
            else:
                return old_val

        result_df                           = input_df.copy()
        if column in result_df.columns:
            result_df[column]               = result_df.apply(_replace, axis=1)
        
        return result_df


    def DFAT(self, df, column, fail=True):
        '''
        Acronym DFAT stands for "DataFrame <df> at column <column>".

        This basically is a method to "safely" select a column of a DataFrame:

        * If all goes well, it returns the Series `df[column]`. 
        
        * However, if the column `column` is not a real column of `df`, then it will catch the KeyError exception and
          then:
           
          * If the `fail` input is True, it will raise a ValueError whose message includes what the real columns of `df` are
          * If `fail` is False, it simply returns None quietly.


        @param df A DataFrame
        @param column An object presumed to be a column of `df`
        @param fail A boolean that determines whether to raise an Exception or simply quietly fail and return None
        '''
        try:
            result_series                                           = df[column]
        except KeyError as ex:
            if fail is True:
                real_columns_str                                    = "[" + ", ".join([str(col) for col in df.columns]) + "]"
                msg                                                 = "'" + str(column) + "' is not a real column of DataFrame. " \
                                                                        + "\nReal columns are: " + real_columns_str
                raise ValueError(msg)
            else:
                return None

        except Exception as ex:
                raise ex
        return result_series

    def count_rows(self, series_fragment):
        '''
        Used when aggregating a DataFrame with column-specific functions, i.e., calling 
        
            `DataFrame.aggregate({col1: function1, col2: function2, ...})

        This method can be one of those functions used as a value in the aggregate's dictionary parameter.

        It will do aggregation by counting the number of rows in `series_fragment`

        @param series_fragment A Pandas Series
        '''
        return len(series_fragment.index)
    
    def list_vals(self, series_fragment):
        '''
        Returns a list of the unique values appearing in the series `series_fragment`
        '''
        if type(series_fragment) != _pd.Series:
            raise ValueError("DataFrameUtils().list_vals is being called with a '" + str(type(series_fragment)) 
                             + "'; should be a Series instead")
        vals_l = list(series_fragment.unique())
        return vals_l

    def enumerate_vals(self, series_fragment, exclude=None, delimeter=", "):
        '''
        Used when aggregating a DataFrame with column-specific functions, i.e., calling 
        
            `DataFrame.aggregate({col1: function1, col2: function2, ...})

        This method can be one of those functions used as a value in the aggregate's dictionary parameter.

        It will do aggregation by returning a delimeter-separate string of all distinct values in `series_fragment`,
        excluding the `exclude` value. 
        
        If the values in `series_fragment` are not strings, they get converted to strings.

        For example, if `exclude` is DataFrameUtils.BLANK_VALUE, it will enumerate only non-blank values

        @param series_fragment A Pandas Series
        @param delimeter a string, used to separate the values in the string being returned. By default it is ", "
        @param exclude A value in the `series_fragment`, representing a value not to be counted. Ignored if it is null, the default.
        '''
        vals_l                  = [str(elt) for elt in self.list_vals(series_fragment)]
        vals_l                  = sorted(vals_l)
        
        if exclude != None:
            vals_l              = [elt for elt in vals_l if elt != exclude]
        return delimeter.join(vals_l)
    
    def most_prevalent_val(self, series_fragment, exclude=None):
        '''
        Used when aggregating a DataFrame with column-specific functions, i.e., calling 
        
            `DataFrame.aggregate({col1: function1, col2: function2, ...})

        This method can be one of those functions used as a value in the aggregate's dictionary parameter.

        It will do aggregation by looking at all distinct values in `series_fragment`,
        (excluding the `exclude` value), and picking up winner that is "most prevalent", i.e., the value that
        occurs the most often in the ``series_fragment``. If there is a tie for which value
        is "most prevalent", then a random one is picked among the equally-prevalent winners.
        
        If the values in `series_fragment` are not strings, they get converted to strings.

        For example, if `exclude` is DataFrameUtils.BLANK_VALUE, it will pick the most prevalent non-blank value

        @param series_fragment A Pandas Series
        @param delimeter a string, used to separate the values in the string being returned. By default it is ", "
        @param exclude A value in the `series_fragment`, representing a value not to be counted. Ignored if it is null, the default.
        '''
        vals_l                  = [str(elt) for elt in self.list_vals(series_fragment)]
        vals_l                  = sorted(vals_l)
        
        if exclude != None:
            vals_l              = [elt for elt in vals_l if elt != exclude]

        one_column_df           = series_fragment.to_frame()
        VAL                     = "VAL"
        one_column_df.columns   = [VAL]
        best_count_so_far       = -1
        best_val_so_far         = None
        for val in vals_l:
            count               = len(one_column_df[one_column_df[VAL]==val])
            if count > best_count_so_far:
                best_count_so_far   = count
                best_val_so_far     = val

        return best_val_so_far
    
    def merge_enumerated_vals(self, series_fragment, exclude=None, delimeter=", "):
        '''
        Used when aggregating a DataFrame with column-specific functions, i.e., calling 
        
            `DataFrame.aggregate({col1: function1, col2: function2, ...})

        This method can be one of those functions used as a value in the aggregate's dictionary parameter.

        It will do aggregation by returning a delimeter-separate string of all distinct values in `series_fragment`,
        excluding the `exclude` value, assuming that the values in `series_fragment` are strings separated
        by the `delimeter`. I.e., it will merge lists into a single list without duplicates

        For example, if `exclude` is DataFrameUtils.BLANK_VALUE, it will enumerate only non-blank values

        @param series_fragment A Pandas Series
        @param delimeter a string, used to separate the values in the string being returned. By default it is ", "
        @param exclude A value in the `series_fragment`, representing a value not to be counted. Ignored if it is null, the default.
        '''
        val_lists_l             = sorted(self.list_vals(series_fragment))
        vals_s                  = set()
        # Merge the lists. We use a set to avoid duplicates
        for a_list_str in val_lists_l:
            a_list              = a_list_str.split(delimeter)
            vals_s              = vals_s.union(set(a_list))
        # Now sort
        vals_l                  = sorted(list(vals_s))
        if exclude != None:
            vals_l              = [elt for elt in vals_l if elt != exclude]
        return delimeter.join(vals_l)

    
    def count_vals(self, series_fragment, exclude=None):
        '''
        Used when aggregating a DataFrame with column-specific functions, i.e., calling 
        
            `DataFrame.aggregate({col1: function1, col2: function2, ...})

        This method can be one of those functions used as a value in the aggregate's dictionary parameter.

        It will do aggregation by counting the number unique values in `series_fragment`, excluding the `exclude` value.
        For example, if `exclude` is DataFrameUtils.BLANK_VALUE, it will count only non-blank values

        @param series_fragment A Pandas Series
        @param exclude A value in the `series_fragment`, representing a value not to be counted. Ignored if it is null, the default.
        '''
        vals_l                  = self.list_vals(series_fragment)
        if exclude != None:
            vals_l              = [elt for elt in vals_l if elt != exclude]
        total = len(vals_l)
        
        return total

    def totals(self, input_df):
        '''
        Collapses and returns DataFrame `input_df` to a single row DataFrame by summing up each column.

        @param `input_df` A DataFrame all of whose columns have numerical values
        '''
        result_df                           = input_df.aggregate(sum).to_frame().transpose()
        result_df.index                     = ["Total"]
        return result_df


    def one_hot_encoding(self, input_df, enum_column, renaming_dict={}, include_totals=True):
        '''
        @param enum_column A string, which should be a column in the input_df parameter. Normally its values would
                            be a limited set of values, like an enum.
        @param input_df A DataFrame
        @param renaming_dict A dictionary whose values define the desired column names in the output for each key,
                        which should be a value in `input_df[enum_column]`. If no such mapping is present in the dictionary,
                        then the desired column name will be assumed to be the original value in `input_df[enum_column]`.
                        This dictionary is optional and is an empty dictionary by default.
        @param include_totals A boolean, which is True by default. If True it will add a column in the output DataFrame
                        that adds all one-hot encoded columns. For example, if we are one-hot encoding "Severity",
                        then having `include_totals==True` would add a column called "All Severity" which has a 1
                        for every row.
        
        Creates and returns a new DataFrame by adding N columns to input_df, where N is the number of unique values
        for under input_df[enum_column]. These N colums have a 0 or 1, where 1 in a new column hot_column indicates 
        that the row has a value in row[enum_column] equal to hot_column.

        Additionally, it returns a OneHotEncodingInfo that describes these changes, in case the caller needs such metadata
        in order to relate the columns of the output to the columns of the input.
        '''
        def _encode(enum_value):
            def _impl(row):
                val                         = row[enum_column]
                if val == enum_value:
                    return 1
                elif self.is_blank(val) and self.is_blank(enum_value):
                    return 1
                else:
                    return 0
            return _impl
            
        result_df                           = input_df.copy()
        enum_values                         = input_df[enum_column].unique()

        # We build build this as a 1-1 relationship with enum_values, potentially renaming. Keys are the 
        # names of hot columns we will use, and values are the enum values in the original `input_df`
        hot_mapping_dict                    = {}
         
        for ev in enum_values:
            if ev in renaming_dict.keys():
                hot_col                     = renaming_dict[ev]
            elif self.is_blank(ev): 
                # Boundary case. Happens sometimes that we get a nan that later gives problems, so get rid of it
                # by replacing it with a proper string.
                hot_col                     = "Null " + str(enum_column)
            else:
                hot_col                     = ev
            hot_mapping_dict[hot_col]   = ev

        info                                = OneHotEncodingInfo(original_column    = enum_column,
                                                                 hot_mapping_dict   = hot_mapping_dict,
                                                                 include_totals     = include_totals)

        if include_totals==True:
            TOTAL                               = info.get_total_column()
            result_df[TOTAL]                    = 0
        for hot_col in hot_mapping_dict.keys():
            ev                              = hot_mapping_dict[hot_col]
            result_df[hot_col]              = input_df.apply(_encode(ev), axis=1)
            if include_totals==True:
                result_df[TOTAL]            = result_df[TOTAL] + result_df[ev]

        return result_df, info    
    
    def collapse_to_N_columns(self, input_df, field_to_flatten, nb_columns_to_create, delimeter):
        '''
        @param field_to_flatten A string, which should be a column in the `fragment_df` parameter. 
        @param input_df A DataFrame
        @param nb_columns_to_create An integer bigger than 0
        @param delimeter A string used to separate values that are concatenated together into a single cell in the
                output DataFrame

        Creates and returns a new DataFrame obtained from `input_df` by "collapsing" rows on the column `field_to_flatten`,
        but without losing content. This means that while the "collapsing" will eliminate the column `field_to_flatten`, the
        content of that columns is preserved by adding N new rows, where N = `nb_columns_to_create` where the content in
        the disappearing `field_to_flatten` column goes.

        Example: Suppose you have this dataframe:

            VULNERABLE ITEM                 CONFIGURATION ITEM          PROOF
            
            VIT7866709	                    blrcswliqpt0007             Fix open port 89
            VIT7866709	                    blrcswliqpt0007             Fix open port 91
            VIT4067153	                    blrcswliqin0005             Bad install at /usr/local/java8
            VIT4067153	                    blrcswliqin0005             Bad install at /usr/local/java8.1
            VIT4067153	                    blrcswliqin0005             Bad install at /usr/local/java8.2
            VIT4067153	                    blrcswliqin0005             Bad install at /usr/local/java8.3

        In this example, there are really only 2 vulnerable items, but each of them has multiple proofs. If
        this function is called with `field_to_flatten`=PROOF and `nb_columns_to_create`=3, then the multiplicities in the
        PROOF column will be distributed onto 3 new columns. 
        
        Of course, the number of multiplicities may be less than 3, as in the case of VIT7866709: it has only 2 proofs. In
        that case the unused new columns will have a blank.

        Conversely, if the number of multiplicities is more than 3, then the as is the case of VIT4067153 (with 4 proofs),
        then the 3rd new column will have all of the remaining content, concatenated with the `delimeter` parameter as
        as separator.

        In the example, if `delimeter`=" | ", then the returned DataFrame will be 
 
            VULNERABLE ITEM     CONFIGURATION ITEM      PROOF #1                            PROOF #2                            Rest of PROOFs
            
            VIT7866709	        blrcswliqpt0007         Fix open port 89                    Fix open port 91                    -
            VIT4067153	        blrcswliqin0005         Bad install at /usr/local/java8     Bad install at /usr/local/java8.1   Bad install at /usr/local/java8.2 | Bad install at /usr/local/java8.3

        '''
        def _distribute_on_N_columns(row):
            '''
            Used to aggregate a grouped-by DataFrame.

            Returns a list of size equal to the `nb_columns_to_create` parameter. In the DataFrame created by collapse_to_N_columns,
            this list will be the values for the new columns for a single row.
            '''
            vals_l                          = list(row[field_to_flatten].unique())
            if len(vals_l) <= nb_columns_to_create:
                nb_columns_to_pad           = nb_columns_to_create - len(vals_l)
                result_l                    = vals_l + [self.BLANK_VALUE]*nb_columns_to_pad
            else:
                cutoff                      = nb_columns_to_create-1
                result_l                    = vals_l[:cutoff]
                rest_of_val                 = delimeter.join(vals_l[cutoff:])
                result_l.append(rest_of_val)
            return result_l

        new_columns                         = []
        for idx in range(nb_columns_to_create-1):
            new_columns.append(field_to_flatten + " #" + str(idx+1))
        new_columns.append("Rest of " + field_to_flatten + "s")

        columns_to_keep                     = [col for col in input_df.columns if col != field_to_flatten]

        # We will group by `columns_to_keep`, so to avoid losing rows due to nan's, need to fill them with blanks.
        # Also avoid nan-s in the `field_to_flatten`
        df0                                 = self.fill_nan(input_df, columns=columns_to_keep + [field_to_flatten])

        # This will produce a DataFrame with 1 column, called "0", whose values are lists of size `nb_columns_to_create`
        COLUMN_CONTAINING_LISTS             = 0
        df1                                 = df0.groupby(columns_to_keep).apply(lambda row: _distribute_on_N_columns(row)).to_frame()

        # Unpack the column containing N lists into N columns of scalars
        df2                                 = df1.copy()
        for idx in range(len(new_columns)):
            col                             = new_columns[idx]
            df2[col]                        = df2.apply(lambda row: row[COLUMN_CONTAINING_LISTS][idx], axis=1)
    
        # Now we are done moving the content out of the `field_to_flatten` column, so we can drop the intermediate column
        # produced by the group-by
        df3                                 = df2.copy()
        df3                                 = df3.drop(COLUMN_CONTAINING_LISTS, axis=1)

        result_df                           = df3.reset_index()

        return result_df 
    
    def _drop_spurious_columns(self, input_df):
        '''
        Creates and returns a DataFrame obtained from `input_df` by dropping columns that Pandas creates
        at various times, such as when loading a DataFrame from Excel, which may lead to the creation
        of the "Unnamed :0" column
        '''
        SPURIOUS_COLUMNS                    = ["Unnamed: 0", "Unnamed: 0.1"] #, 'Unnamed: 0.1', 'Unnamed: 0']
        columns_to_drop                     = []
        for col in SPURIOUS_COLUMNS:
            if col in input_df.columns:
                columns_to_drop.append(col)

        result_df                           = input_df.drop(columns=columns_to_drop)
        return result_df
    
    def load_excel(self, path, sheet_name="Sheet1"):
        '''
        Creates and returns a DataFrame by loading an Excel spreadsheet, removing any spurious columns if needed.
        '''
        df0                                 = _pd.read_excel(path, sheet_name=sheet_name)
        df1                                 = self._drop_spurious_columns(df0)
        return df1

    def re_index(self, input_df):
        '''
        Helper method to beautify some DataFrames for which the index has been re organized out, so it does not read
        like consecutive integers 1,2,3,...

        This method returns a DataFrame obtained by resetting the index in the `input_df`.
        '''
        output_df                           = input_df.reset_index()
        COLUMNS_TO_DROP                     = ["index"]
        for col in COLUMNS_TO_DROP:
            if col in output_df.columns:
                output_df                   = output_df.drop("index", axis=1)
        return output_df
    
    def slim_so_field_is_unique(self, input_df, fieldname):
        '''
        Sometimes we want to drop columns from a DataFrame so that a particular column has unique values, ie.,
        it can be a primary key.

        This method achieves that by removing a minimalist set of columns from `input_df` that cause the
        duplication for values in column `fieldname`, and returning a de-duplicated DataFrame with exactly 
        1 row per `fieldname` value.
        
        @param input_df A DataFrame, with at least two columns

        @param fieldname A string, which must be a column in `input_df`
        '''
        columns_to_drop                         = self._find_columns_causing_most_duplicates(input_df, fieldname)
        columns_to_keep                         = [col for col in input_df.columns if not col in columns_to_drop]
        nodups_df                               = input_df[columns_to_keep].drop_duplicates()
        return nodups_df

    def slim_retaining_interesting_fields(self, input_df, field_to_slim_to, interesting_fields):
        '''
        This utility is in the same spirit as `self.slim_so_field_is_unique`, i.e., the spirit of eliminating a
        minimal set of columns until the `field_to_slim_to` is unique, i.e., can be a primary key if duplicates
        are dropped.

        Where this method differs from `self.slim_so_field_is_unique` is that it is contrained to not drop
        the  columns listed in `interesting_fields`, which results therefore in some possible duplication
        of values for `field_to_slim_to` in multiple rows. 

        @param input_df A DataFrame, from which this method creates and returns a "slimmed down" version with probably
                        fewer rows.
        @param field_to_slim_to A string, which must be a column in `input_df`
        @param interesting_fields A list of strings, each of which must be a column in `input_df` with string values
        '''
        strict_slim_df                              = self.slim_so_field_is_unique(input_df, field_to_slim_to)
        slim_columns                                = list(strict_slim_df.columns)
        # Avoid having a column duplicated by only adding interesting_fields not already in the slim columns
        columns_to_add                              = [elt for elt in interesting_fields if not elt in slim_columns]
        result_df                                   = input_df[slim_columns + columns_to_add].drop_duplicates()
        result_df                                   = self.fill_nan(result_df, interesting_fields, fill_value="")
        return result_df

    def slim_collapsing_interesting_fields(self, input_df, field_to_slim_to, interesting_fields,
                                           collapsing_methods_dict = {}):
        '''
        This utility is in the same spirit as `self.slim_retaining_interesting_fields`, i.e., drop a minimalist
        set of columns so that we get as close as possible to have `field_to_slim_to` be a primary key, while
        not dropping the  columns listed in `interesting_fields`.

        The difference with `slim_retaining_interesting_fields` is that this method does succeed at making
        `field_to_slim_to` a primary key, by "collapsing" the values of columns in `interesting_fields`.
        
        By "collapsing" we mean that for each column `col` in `interesting_fields`, the resulting DataFrame 
        has two columns:

        * A column `col` whose value is a "collapse" of the unique values
                that `input_df` has in that column for the given value of `field_to_slim_to`. The collapsing
                method by default is to do a comma-separated enumeration, unless a different method
                is specificed for `col` in collapsing_methods_dict.
         
        * A columnn called `"# {col}"` whose value is an integer representing the number of unique values
                that `input_df` has in that column for the given value of `field_to_slim_to`
        
        @param input_df A DataFrame, from which this method creates and returns a "slimmed down" version with probably
                        fewer rows.
        @param field_to_slim_to A string, which must be a column in `input_df`
        @param interesting_fields A list of strings, each of which must be a column in `input_df` with string values
        @param collapsing_methods_dict A dict, which is empty by default. Keys are strings taken from `interesting_fields`,
                and values are functions that are used to collapse, with a signature like

                        lambda(series_fragment)

                where `series_fragment` is a Pandas Series, and the return value is a string or scalar suitable to use
                as a collapsed value. If the dict has no value for a given `interesting_fields` member, by default the
                collapse is done using `DataFrameUtils().enumerate_vals`.
        '''
        base_df                                     = self.slim_retaining_interesting_fields(input_df, field_to_slim_to, interesting_fields)

        columns_for_grouping                        = [col for col in base_df.columns if not col in interesting_fields]

        # GOTCHA If any column in columns_for_grouping is nan, then the groupby will ignore such rows and we will get the wrong
        #       result. So fill them up
        base_df                                     = self.fill_nan(base_df, columns=columns_for_grouping)

        uncollapsed_df                              = base_df.copy()
        spec                                        = {}
        for col in interesting_fields:
            NB_COL                                  = "# " + col
            spec[NB_COL]                            = self.count_vals
            if col in collapsing_methods_dict.keys():
                method                              = collapsing_methods_dict[col]
                spec[col]                           = method

            else:
                spec[col]                           = self.enumerate_vals
            uncollapsed_df[NB_COL]                  = uncollapsed_df[col]
            

        if len(interesting_fields) > 0:
            collapsed_df                            = uncollapsed_df.groupby(columns_for_grouping).aggregate(spec).reset_index()
        else:
            collapsed_df                            = uncollapsed_df
        collapsed_df                                = collapsed_df.sort_values(by=field_to_slim_to)
        return collapsed_df

    def explore_a_collapse(self, input_df, primary_key_fields, collapsing_fields):
        '''
        Assists in DataAnalysis by giving creating and returning a DataFrame that informs whether collapsing
        some fields is a good idea.

        @param input_df A DataFrame for which we are doing data analysis, and for which we hypothesize that
                we could collapse its columns listed in `collapsing_fields` for each combination of values in its
                columns `primary_key_fields`.

        The hypothesis tested by this method is that that we aspire to having a report showing a row for
        each value combination of the columns in `primary_key_fields`, while collapsing via enumeration the columns in 
        `collapsing fields`. From a usability perspective, such hypothesis is valid only if the size of the collapsed
        values is small per row, e.g., ~2-20 as opposed to 500-1000s.

        To validate or refute this hypothesis, this method performs the hypothesized collapse just retaining the columns
        in `primary_key_fields` and `collapsing_fields`, and shows for each column `col` in `input_df` in `collapsing_fields`
        it shows 2 columns in the resulting DataFrame:

        * A column `col` showing the enumerated collapse of column `col` in `input_df`

        * A column `# {col}` showing the number of unique values that were collapsed
        '''
        base_df                                     = input_df.copy()
        spec                                        = {} # Used for aggregation after grouping by the `primary_key_fields`
        collapsing_counts                           = []
        for col in collapsing_fields:
            count_col                               = "# " + col
            collapsing_counts.append(count_col)
            base_df[count_col]                      = base_df[col]
            spec[count_col]                         = self.count_vals
            spec[col]                               = self.enumerate_vals


        collapsed_df                                = base_df.groupby(primary_key_fields).aggregate(spec)

        # Sort in descending order by the collapsing fields
        collapsed_df                                = collapsed_df.sort_values(by=collapsing_counts, ascending=False)
        collapsed_df                                = collapsed_df.reset_index()
        
        return collapsed_df
        
    def check_multiplicity(self, input_df, pk_fieldname, multiplicity_fieldname):
        '''
        Helper method used to explore whether a field `multiplicity_fieldname` is preventing another field 
        `pk_fieldname` from serving as a "primary key", i.e., have a unique value per row in `input_df`

        The help provided by this method is in the form of a DataFrame that it creates and returns, which shows
        the multiplicities in ascending order, i.e., for each value of the `pk_fieldname` column in `input_df`
        that corresponds to multiple values in the `multiplicity_fieldname`, the returned DataFrame shows the number
        of such multiplicities, as an integer.

        @param input_df A DataFrame
        @param pk_fieldname A column in `input_df`
        @param multiplicity_fieldname A column in `input_df`
        '''
        spec                                        = {multiplicity_fieldname: self.count_vals}
        #duplicates_df                               = input_df.groupby([pk_fieldname]).count()[multiplicity_fieldname].to_frame()
        duplicates_df                               = input_df.groupby([pk_fieldname]).aggregate(spec)
        duplicates_df.columns                       = ["# items"]
        duplicates_df                               = duplicates_df[duplicates_df["# items"] > 1]
        duplicates_df                               = duplicates_df.sort_values(by=["# items"], ascending=False)
        return duplicates_df

    def _find_columns_causing_most_duplicates(self, input_df, fieldname):
        '''
        Helper method used to find columns that cause "duplicates" for the value of column `fieldname`
        
        To assist in "removing duplicates", this method identifies the columns in `input_df` which cause duplicates.
        
        The logic is implemented recursively: first find the columns that cause the "most duplicates", obtain a
        de-duplicated DataFrame from that, and use to find the next round of columns causing "most duplicates"
        until ther are no more.
        
        @param input_df A DataFrame, with at least two columns

        @param fieldname A string, which must be a column in `input_df`
        
        @returns A list of strings, which are a subset of columns of `input_df` that "cause" duplicates. I.e., if such
                columns were removed from `input_df` and `DataFrame::drop_duplicates()` called, then there would be exactly 1 row
                per value of `input_df.
        ''' 

        # Find a column different than `fieldname` to keep in the groupby, while we drop the rest
        ANY_COLUMN                                  = [col for col in input_df.columns if col !=fieldname][0]
        duplicates_df                               = input_df.groupby([fieldname]).count()[ANY_COLUMN].to_frame()
        duplicates_df.columns                       = ["# items"]
        duplicates_df                               = duplicates_df[duplicates_df["# items"] > 1]
        duplicates_df                               = duplicates_df.sort_values(by=["# items"], ascending=False)
        if len(duplicates_df.index)==0:
            # There are no duplicates. It is important to return here to avoid an infinite recursion problem,
            # since later on we will recourse to successively harvest lists of columns causing duplicates.
            return []
        # Else we filter on the first value, since that has the most duplicates
        duplicated_val                              = duplicates_df.index[0]
        
        duplicated_val_df                           = input_df[input_df[fieldname]==duplicated_val]
        
        # We know problem_vis_df has at least 2 rows and that they differ in at least some columns, since
        # otherwise we would have returned an empty list in the logic above.
        #
        # Find what those columns are for these first 2 rows, which via sorting we know are the ones with the most
        # duplicates
        row_0                                       = duplicated_val_df.iloc[0]
        row_1                                       = duplicated_val_df.iloc[1]
        most_differences_cols                       = []
        for col in duplicated_val_df.columns:
            val_0                                   = row_0[col]
            val_1                                   = row_1[col]
            if val_0 != val_1:
                most_differences_cols.append(col)
        
        columns_to_keep                             = [col for col in input_df.columns if not col in most_differences_cols]
        if len(columns_to_keep) == len(input_df.columns):
            # This should never happen - our list of columns should be getting smaller, so if it does not,
            # the recursion will be infinite and there is a bug in the earlier code that was supposed to return
            # in such situations so that we never get here
            raise Exception("Infinite recursion error in 'find_columns_causing_most_duplicates': column size not "
                            + "reduced. Was supposed to have a non-empty list of colums driving the duplicates: ["
                            + ", ".join(most_differences_cols) + "].")
        first_deduplicated_df                       = input_df[columns_to_keep].drop_duplicates()
        
        other_differences_cols                      = self._find_columns_causing_most_duplicates(first_deduplicated_df, fieldname)
        
        return most_differences_cols + other_differences_cols    
    
    def apply_multiple_columns(self, input_df, column_names, lambda_function):
        '''
        Helper method used when we want to add or change multiple columns in `input_df` with a single lambda.

        This is generalization of the `DataFrame.apply` method. For example, if we wanted to add
        a single column called "FOO" with a lambda called "BAR", one normally does:

            input_df["FOO"]         = input_df.apply(lambda row: BAR(row), axis = 1)

        If BAR return a single scalar, that would be the value of the "FOO" column.

        Our generalization is for setting multiple columns. Say you want to set columns "FOO 1", "FOO 2", and "FOO 3", 
        and you have a lambda "BAR_3d" that returns triples of scalars, like a tuple of size 3.
        
        Then this method does what one would like to have happened if DataFrames supported something like this syntax:

            input_df[["FOO 1", "FOO 2", "FOO 3"]] = = input_df.apply(lambda row: BAR_3d(row), axis = 1)

        It would be nice if Pandas supported that, but it does not. So this utility function provides that
        functionality.

        It creates and returns a new DataFrame based on `input_df` to which multiple columns are added based on a single
        tuple-valued lambda.

        @param `input_df` A DataFrame for which we want to make a copy and add multiple columns to such copy.

        @param column_names A list of columns to add to the copy of `input_df` we are returning from this method.

        @param lambda_function A function that takes as an input a `row` from `input_df` and returns a tuple of values
                whose length must equal that of `column_names`
        '''
        
        # This returns a DataFrame with a single column called 0, and all values in that unique column are 
        # tuples
        # 
        column_of_tuples_df                             = input_df.apply(lambda row: lambda_function(row), axis=1).to_frame()

        # Now we unpack each tuple at a time, and use it to create the new (or modified) columns
        UNIQUE_COLUMN                                   = 0
        df0                                             = input_df.copy()
        for idx in range(len(column_names)):
            col                                         = column_names[idx]
            df0[col]                                    = column_of_tuples_df.apply(lambda row: row[UNIQUE_COLUMN][idx], axis=1)
        
        result_df                                       = df0
        return result_df

    def diff_labels(self, left_df, right_df, pk_column):
        '''
        Returns 4 lists:

        * Columns in left_df not in right_df
        * Columns not in left df in right_df
        * Unique value of column `pk_column` in left_df not in right_df
        * Unique value of column `pk_column`  not in left_df in right_df
        '''
        left_cols                           = set(left_df.columns)
        right_cols                          = set(right_df.columns)
        left_pks                            = set(left_df[pk_column].unique())
        right_pks                           = set(right_df[pk_column].unique())

        in_out_cols                         = list(left_cols.difference(right_cols))
        out_in_cols                         = list(right_cols.difference(left_cols))
        in_out_pks                          = list(left_pks.difference(right_pks))
        out_in_pks                          = list(right_pks.difference(left_pks))

        return in_out_cols, out_in_cols, in_out_pks, out_in_pks
    
    def intersect_labels(self, left_df, right_df, pk_column):
        '''
        Returns 2 lists:

        * Columns in left_df and in right_df
        * Unique values of column `pk_column` in left_df and in right_dff
        '''
        left_cols                           = set(left_df.columns)
        right_cols                          = set(right_df.columns)
        left_pks                            = set(left_df[pk_column].unique())
        right_pks                           = set(right_df[pk_column].unique())

        intersect_cols                      = list(left_cols.intersection(right_cols))
        intersect_pks                       = list(left_pks.intersection(right_pks))

        return intersect_cols, intersect_pks

    def restore_losses(self, backup_df, damaged_df, pk_column, columns_to_restore):
        '''
        Utility used to restore lost content when DataFrames get generated on a cadence, and due to 
        some processing error the information in the prior version of a DataFrame does not fully make it to the new version.

        This method will create and returned a new DataFrame with the same labels as `damaged_df`. Assumptions are:

        * `pk_column` is a column in both `backup_df` and `damaged_df`
        * `columns_to_restore` is a list of column labels that exist in both `backup_df` and `damaged_df`
        * `pk_column` is a primary key for both `backup_df` and `damaged_df`. For a value K of `pk_column`,
            if K exists in both `backup_df` and `damaged_df`, we use the notation backup[K] and damaged[K] to refer to the
            unique row in the respective DataFrames that has K as the value of the `pk_column`.

        Then the method will return a new DataFrame restored_df with these characteristics:

        * Has the same same labels as `damaged_df`

        * For any primary key K in both DataFrames and any column C in `columns_to_restore`, if damaged[K][C]
          is blank or equal to DataFrameUtils.BLANK_VALUE, then restored[K][C] is equal to
          backup[K][C]. Otherwise it is equal to damaged[K][C]
        '''
        backup_pks                              = list(backup_df[pk_column].unique())
        def _has_content(row, a_column):
            val                                 = row[a_column]
            if self.is_blank(val) or val == self.BLANK_VALUE:
                return False
            else:
                return True
        def _restore(row, a_column):
            pk                                  = row[pk_column]
            restored_val                        = row[a_column] # Default is to "leave as is" , unless we change it below

            if pk in backup_pks:
                backup_row                      = backup_df[backup_df[pk_column]==pk].iloc[0]
                if _has_content(backup_row, a_column) and not _has_content(row, a_column):
                    restored_val                = backup_row[a_column]
            
            return restored_val
            
        restored_df                             = damaged_df.copy()
        for col in columns_to_restore:
            if col in backup_df.columns and col in damaged_df.columns:
                restored_df[col]                = restored_df.apply(lambda row: _restore(row, col), axis=1)

        return restored_df

class OneHotEncodingInfo:

    def __init__(self, original_column, hot_mapping_dict, include_totals):
        '''
        Data structure used to remember some of the relationships between the columns of the input vs output DataFrames
        processed by the method DataFrameUtils().one_hot_encoding(-)

        @param hot_mapping_dict A dictionary. Keys are the names of the one-hot columns that were added and values
                are the enum values they correspond to. Usually key and value are the same, but they may differ if
                there is renaming happening as part of the processing of DataFrameUtils().one_hot_encoding(-)
        '''
        self.original_column                = original_column
        self.hot_mapping_dict               = hot_mapping_dict
        self.include_totals                 = include_totals


    def get_total_column(self):
        '''
        Returns the name of the column that has torals for the one-hot encoded field in the DataFrame produced by 
        DataFrameUtils().one_hot_encoding(-)
        '''
        if self.include_totals == False:
            raise ValueError("This one-hot encoding did not include a totals column")
        
        return "All " + self.original_column
        
    def get_one_hot_columns(self):
        '''
        Returns a list of the columns that were added by the DataFrameUtils().one_hot_encoding(-) process
        '''
        columns                             = list(self.hot_mapping_dict.keys())
        if self.include_totals == True:
            columns.append(self.get_total_column())

        return columns

    def get_slice(self, encoded_df, one_hot_column):
        '''
        Used in situations when we need to "reverse engineer" a one-hot encoding and, for example, get counts of 
        vulnerable items from knowing an enum_value. Typically this is done in de-duplication situations.

        Example:

            Suppose a report is producing sub-totals of vulnerable items per product, for various severity levels.
            Suppose the report also aspires to display a row of totals at the bottom, across products.

            Since the "Severity" column has values like "1 - Critical" and "2 - High", a one-hot-encoded DataFrame would
            have columns called "1 - Critical" and "2 - High", in addition to the "Severity" column.

            In order to get the total number of vulnerabilities for "1 - Critical", say, it is not correct to add the
            sub-totals in the report for the "1 - Critical", since a vulnerability might be double counted if 
            it pertains to multiple products.

            What has to be done, instead, is but a slice of the DataFrame to those for which the "Severity" column
            has the value "1 - Critical", and count the length of that index. To assist with that, this method
            will return such a slice given an `enum_value` of "1 - Critical"

        @param encoded_df A DataFrame that has gone through one-hot encoding by DataFrameUtils().one_hot_encoding(-),
                            the result of which also produced self.

        @param enum_value One of the columns in `encoded_df` that was created by the encoding
        '''
        DFU                                 = DataFrameUtils()

        if self.include_totals and one_hot_column == self.get_total_column():
            # This is something like the "All Severity" column that is created by one-hot encoding the "Severity" column.
            # In that case, the slice of pertinent values is everything
            slice_df                        = encoded_df
        elif one_hot_column in self.hot_mapping_dict.keys():
            enum_value                      = self.hot_mapping_dict[one_hot_column]

            # GOTCHA - Bug 1508
            #   We would like to do something like 
            #
            #       slice_df = encoded_df[encoded_df[self.original_column]==enum_value]
            #
            #   but that fails in enum_value is nan: rows that have nan are not selected since "nan == nan"
            #   evaluates to false.
            #
            #   So instead we use this special function:
            def _value_matches(enum_column, enum_value):
                def _impl(row):
                    val                         = row[enum_column]
                    if val == enum_value:
                        return True
                    elif DFU.is_blank(val) and DFU.is_blank(enum_value):
                        return True
                    else:
                        return False
                return _impl

            #slice_df                        = encoded_df[encoded_df[self.original_column]==enum_value] # Doesn't work for nan
            slice_df                        = encoded_df[encoded_df.apply(_value_matches(self.original_column, enum_value),
                                                                          axis = 1)]
        else:
            raise ValueError("'" + one_hot_column + "' is not a valid column name added by one-hot encoding")
        
        return slice_df