import pandas                                                           as _pd

from conway.dataset.dataset_content                        import DataSetContent
from conway.dataset.slice_definition                       import SliceDefinition

class DataFrameDataSetContent(DataSetContent):

    '''
    :param :class:`DataFrame <pandas.DataFrame>` data_df:
    '''
    def __init__(self, data_df: _pd.DataFrame):
        super().__init__()
        self.data_df                                    = data_df


    def filter(self, slice_def: SliceDefinition) -> DataSetContent:
        filtered_df                                     = self.data_df.copy()
        for constraint in slice_def.filters_to_apply:
            column                                      = constraint.field.name
            if column in list(filtered_df.columns):
                filtered_df                             = filtered_df[filtered_df[column].isin(constraint.allowed_values)]

        result                                          = DataFrameDataSetContent(data_df = filtered_df)

        return result




