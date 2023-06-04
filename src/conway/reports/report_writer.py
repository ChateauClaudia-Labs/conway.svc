from conway.application.application                import Application
from conway.observability.logger                   import Logger

from conway.util.dataframe_utils                   import DataFrameUtils

class ReportWriter():

    def __init__(self):
        '''
        Utilities leveraged in the creation of multiple reports
        '''

    def populate_excel_worksheet(self, report_df, workbook, worksheet,
                                    widths_dict = {}, freeze_row_nb=1, freeze_col_nb=1):
        '''
        Helper function to format nicely a report (i.e., set Excel column widths, colors for column headers, and other
        such formatting)
        '''
        DFU                                             = DataFrameUtils()
        clean_df                                        = DFU.re_index(report_df)
        columns                                         = list(clean_df.columns)
        # Set column widths
        for jdx in range(len(columns)):
            xl_column                                   = jdx
            header                                      = columns[jdx]
            width                                       = 12 # Default value
            if header in widths_dict.keys():
                width                                   = widths_dict[header]

            worksheet.set_column(xl_column, xl_column, width)
        
        ROOT_FMT                                        = {'text_wrap': True, 'valign': 'top', 'border': True, 
                                                           'border_color': Palette.WHITE}
        HEADER_FMT                                      = ROOT_FMT | {'bold': True, 'font_color': Palette.WHITE, 
                                                                        'align': 'center','border_color': Palette.WHITE, 
                                                                        'right': True, 'fg_color':     Palette.DARK_BLUE}
        
        header_fmt                                      = workbook.add_format(HEADER_FMT)

        # Now write the headers
        xl_row                                          = 0
        for jdx in range(len(columns)):
            xl_col                                      = jdx
            header                                      = columns[jdx]
            try:
                worksheet.write(xl_row, xl_col, header, header_fmt)
            except Exception as ex:
                Application.app().log("Unable to write column header '" + str(header) + "'; for reference the columns are '"
                                      + "', '".join([str(col) for col in columns]),
                                      log_level = Logger.LEVEL_INFO)
                raise ex


        # Now write the content
        for row in clean_df.iterrows():
            row_nb                                      = row[0]
            row_content                                 = row[1]
            xl_row                                      = row_nb + 1 # Add 1 since header already took 1 row
            for jdx in range(len(columns)):
                col                                     = columns[jdx]
                xl_col                                  = jdx
                val                                     = row_content[col]

                fmt_dict                                = ROOT_FMT.copy()
                if row_nb%2 == 0:
                    fmt_dict                            |= {'bg_color': Palette.LIGHT_BLUE}
                fmt                             = workbook.add_format(fmt_dict)
                try: # This try is just to help put a breakpoint in the debugger if this line ever fails. We don't really handle the exception
                    worksheet.write(xl_row, xl_col, val, fmt)
                except Exception as ex:
                    Application.app().log("Unable to write column header '" + str(header) + "'; for reference the columns are '"
                                        + "', '".join([str(col) for col in columns]))
                    raise ex

        # Freeze panes & set zoom to 85%
        worksheet.freeze_panes(freeze_row_nb, freeze_col_nb)
        worksheet.set_zoom(85)

class Palette():

    # Static colors.
    DARK_BLUE                   = '#0070C0'
    VERY_DARK_BLUE              = '#002060'
    LIGHT_BLUE                  = "#E1F2FF"
    LIGHT_STEEL                 = "#DCE6F1"
    WHITE                       = '#FFFFFF'
    GREEN                       = '#00B050'
    DARK_GREEN                  = '#548235'
    LIGHT_GREEN                 = '#E2EFDA' # '#E5EDD3' # '#EBF1DE'
    DARK_GREY                   = '#808080'
    VERY_DARK_GREY              = "#606060"
    LIGHT_GREY                  = '#F2F2F2' # '#E8E8E8
    ORANGE                      = '#FF9900'

    DARK_PURPLE                 = "#7030A0"
    LIGHT_PURPLE                = "#ECDFF5"

    RED                         = "#FF0000"
    DARK_RED                    = "#A80000"
    TEAL                        = "#31869B"


    