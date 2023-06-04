
import datetime                                                             as _dt

class Timestamp():

    FORCED_TODAY                                                            = None
    '''
    This static flag is null by default. If not null, it should be a string in the timestamp format
    "YYMMDD", and then it will be used to drive what is returned by the method self.today(-).

    This plays a role in test cases, where we need a deterministic response to the invocation of the
    self.today(-) method.
    '''

    def __init__(self, timestamp):
        '''
        Class to provide services to manipulate dates represented in
        the "timestamp" format in which a date is represented as a string "YYMMDD".

        For example, "230421" represents the 21st of April of 2023.

        It supports the ability to map back and forth to these other ways of represeneting dates:

        * A datetime.datetime object

        * A "Snapshot", which is a concept this class introduced where dates are represented like "APR05" to mean
            April 5th. Typical use case is as column headers in reports.

        * An "Excel date", which is a concept this class uses for formats "YY-MM-DD". Typical use case is as the value
          of date columns of an Excel spreadsheet.

        * An "Excel int", which is a concept where dates in Excel as represented as numbers, counting from December 31, 1899.
          For example, 45077 would represent May 31, 2023.

        @timestamp A string reprsenting a date in the forma "YYMMDD"
        '''
        self.timestamp                      = timestamp

    def today():
        '''
        :return: a new Timestamp object as of the day when this method is invoked, unless the system deployment
        has overruled this by setting Timestamp.FORCED_TODAY, in which case the latter is used to create
        the returned Timestamp.

        :rtype: Timestamp
        '''
        if Timestamp.FORCED_TODAY is None:
            now                             = _dt.datetime.now()
            return Timestamp.from_datetime(now)
        else:
            return Timestamp(Timestamp.FORCED_TODAY)

    def from_datetime(a_datetime):
        '''
        Constructs and returns a Timestamp object based on the datetime `dt` parameter.

        @param a_datetime A datetime.datetime object
        '''
        ts                                  = a_datetime.strftime("%y%m%d")
        return Timestamp(ts)

    def from_snapshot(self, snapshot):
        '''
        Constructs and returns a new Timestamp object based on a date given in `snapshot` format.
        An example of the snapshot format is "APR14" to represent April 14. The
        snapshot format does not explicity include a year, only the month and year, so
        the returned Timestamp will use the same year as self.

        @param snapshot A 5-character string representing a date with a 3-letter acronym for the month followed by a 
            2-integer number for the day. For example, "FEB02" means the 2nd of February.
        '''
        date_in_1900                        = _dt.datetime.strptime(snapshot, "%b%d")
        month                               = date_in_1900.month
        day                                 = date_in_1900.day
        year                                = self.year()
        a_datetime                          = _dt.date(year=year, month=month, day=day)
        return Timestamp.from_datetime(a_datetime)
    
    def to_snapshot(self):
        '''
        Returns a string that represents the timestamp in `snapshot` format.
        An example of the snapshot format is "APR14" to represent April 14. The
        snapshot format does not explicity include a year, only the month and year.
        '''
        dt                                  = self.as_date()
        snapshot                            = dt.strftime("%b%d").upper() 
        return snapshot

    def from_excel_date(excel_date):
        '''
        Constructs and returns a new Timestamp object based on a date given in Excel date format.
        An example of the snapshot format is "23-04-14" to represent April 14, 2023. 

        @param snapshot A string representing a date in the format "YY-MM-DD".
        '''
        date_dt                             = _dt.datetime.strptime(excel_date, "%y-%m-%d")
        return Timestamp.from_datetime(date_dt)
    
    def to_excel_date(self):
        '''
        Returns a string that represents the timestamp in Excel date format.
        An example of the snapshot format is "23-04-14" to represent April 14, 2023. 

        @param snapshot A string representing a date in the format "YY-MM-DD".
        '''
        date_dt                             = self.as_date()
        date_xl                             = date_dt.strftime("%y-%m-%d")
        return date_xl
    
    def from_excel_int(date_xl_int):
        '''
        Creates and returns a Timestamp object from Excel in dates like 45043, which in Excel represents
        the date April 30, 2023. 
        
        If the parameter `date_xl_int` is not an int in that range of January 1, 2000 to December 31, 2099, then it 
        raises a ValueError.

        @param date_xl_int An int representing an Excel date, between 36526 and 73050, that represent January 1st 2000 and
                December 31 2099, respectively.
        '''
        excel_zero_dt                       = _dt.datetime(1899, 12, 30).date()
        min_supported_dt                    = _dt.datetime(2000, 1, 1).date()
        max_supported_dt                    = _dt.datetime(2099, 12, 31).date()
        min_xl_int                          = (min_supported_dt - excel_zero_dt).days
        max_xl_int                          = (max_supported_dt - excel_zero_dt).days
        if not type(date_xl_int)==int or date_xl_int < min_xl_int or max_xl_int < date_xl_int:
            return ValueError("Bad in put '" + str(date_xl_int) + "': should be an int between 36526 and 73050 to represent "
                                " a date between January 1st 2000 and December 31 2099")

        date_dt                         = excel_zero_dt + _dt.timedelta(date_xl_int)
        return Timestamp.from_datetime(date_dt)


    def as_date(self):
        '''
        Returns a `datetime.date` object equivalent of self
        '''
        dt                                   = _dt.datetime.strptime(self.timestamp, "%y%m%d").date()
        return dt
    
    def year(self):
        '''
        Returns an integer, corresponding this Timestamp's year.
        '''
        dt                                  = self.as_date()
        return dt.year
    
    def month(self):
        '''
        Returns an integer, corresponding this Timestamp's month.
       '''
        dt                                  = self.as_date()
        return dt.month
    
    def day(self):
        '''
        Returns an integer, corresponding this Timestamp's day.
        '''
        dt                                  = self.as_date()
        return dt.day
    
    def date_from_excel_int(self, date_as_int):
        '''
        Converts and returns an int like 45043 to an equivalent "YYYY-MM-DD" string timestamp.
        For example, since Excel count dates as starting on December 30, 1899, an int like 45043 represents
        April 30, 2023, this method would return "2023-04-30" if `date_as_int` is 45043.
        
        If the parameter `date_as_int` is not an int in that range of January 1, 2000 to December 31, 2099, then it 
        returns it without change. These limits are to avoid situations with the parameter represented something else
        (like a time of the day, with many more significant digits)
        '''
        excel_time_zero = _dt.datetime(1899, 12, 30).date()
        min_date_supported = _dt.datetime(2000, 1, 1).date()
        max_date_supported = _dt.datetime(2099, 12, 31).date()
        min_date_as_int = (min_date_supported - excel_time_zero).days
        max_date_as_int = (max_date_supported - excel_time_zero).days
        if not type(date_as_int)==int or date_as_int < min_date_as_int or max_date_as_int < date_as_int:
            return date_as_int
        else:
            date = excel_time_zero + _dt.timedelta(date_as_int)
            date_ts = date.strftime("%Y-%m-%d")
            return date_ts