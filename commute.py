import pymysql, tokens_and_addresses, time
import pandas as pd
from pandas.io import sql
import dbConnector

class Commute:
    """
    Returns lists of dates and associated commute times between two locations

    Attributes:
        date_list                    List of date/time for particular commute time records.
        drive_time_from_home_list    List of commute times from home to destination.
        drive_time_to_home_list      List of commute times from destination to home.
    """
    date_list = []
    drive_time_start_to_dest_list = []
    drive_time_avg_from_home_list = []
    drive_time_avg_to_home_list = []
    drive_time_stdev_from_home_list = []
    drive_time_stdev_to_home_list = []
    analysis_result_str_list = []
    analysis_result_min_max_list = []

    def __init__(self, start_location_id, dest_location_id):
        self.start_location_id = start_location_id
        self.dest_location_id = dest_location_id
        self.session = dbConnector.createSession()

    def get_commute_data(self,start_id, dest_id, num_records):
        dbConnector.get_commutes(self.session)
        dbConnector.get_commutes_path(self.session, start_id, dest_id)

        start_time = time.time()

        date_list = []
        self.drive_time_from_home_list = commute_df[self.from_home_db_column].tolist()
        self.drive_time_to_home_list = commute_df[self.to_home_db_column].tolist()

        for row in commute_df.itertuples():
            year = date_formatter(row.year)
            month = date_formatter(row.month)
            day = date_formatter(row.day)
            hour = date_formatter(row.hour)
            minute = date_formatter(row.minute)
            date = '{}-{}-{} {}:{}'.format(year, month, day, hour, minute)
            date_list.append(date)

        self.date_list = date_list

        print('Total time: ', time.time() - start_time)

        conn.close()

    def get_commute_data_by_day(self, num_records, day_code):
        '''
        Retrieves commute data for a particular day of the week
        from database and assigns data to date_list, drive_time_from_home_list
        and drive_time_to_home_list.

        day code explanation:  0:Monday-6:Sunday

        :param num_records: Number of database records to return
        :type num_records: int

        :param day_code: Code for a particular day of the week or class of day (weekday/weekend)
        with the following format: 0:Monday-6:Sunday, 7:AllDays, 8:OnlyWeekdays, 9:OnlyWeekends
        :type day_code: int
        '''

        conn = pymysql.connect(host=tokens_and_addresses.sql['Host'], port=tokens_and_addresses.sql['Port'],
                               user=tokens_and_addresses.sql['Username'], passwd=tokens_and_addresses.sql['Password'],
                               db=tokens_and_addresses.sql['Database'])
        seconds_in_week = 60*60*24*7
        epoch_time_week_ago = time.time()-seconds_in_week

        if (day_code >= 0 and day_code <= 6):
            query = "select * from {} " \
                    "where day_code={} and epoch_time>{}" \
                    "order by hour asc, minute asc " \
                    "limit {}".format(self.table, day_code, epoch_time_week_ago, str(num_records))

        commute_df = sql.read_sql(query, con=conn)

        start_time = time.time()

        self.drive_time_from_home_list = commute_df[self.from_home_db_column].tolist()
        self.drive_time_to_home_list = commute_df[self.to_home_db_column].tolist()

        date_list = []

        for row in commute_df.itertuples():
            hour = date_formatter(row.hour)
            minute = date_formatter(row.minute)
            date = '{}:{}'.format(hour, minute)
            date_list.append(date)

        self.date_list = date_list

        print('Total time: ', time.time() - start_time)

        conn.close()

    def get_commute_average(self, num_records, day_code):
        '''
        Retrieves list of commute data average and standard deviation for a particular day of the week or
        class of day (weekday/weekend) from database and assigns data to date_list, drive_time_from_home_list
        and drive_time_to_home_list.  Average and standard deviation is computed on 20 minute increments.
        Error bar length is equal to one standard deviation representing 68.3% of samples.

        day code explanation:  0:Monday-6:Sunday, 7:AllDays, 8:OnlyWeekdays, 9:OnlyWeekends

        :param num_records: Number of database records to return
        :type num_records: int

        :param day_code: Code for a particular day of the week or class of day (weekday/weekend)
        with the following format: 0:Monday-6:Sunday, 7:AllDays, 8:OnlyWeekdays, 9:OnlyWeekends
        :type day_code: int
        '''

        conn = pymysql.connect(host=tokens_and_addresses.sql['Host'], port=tokens_and_addresses.sql['Port'],
                               user=tokens_and_addresses.sql['Username'], passwd=tokens_and_addresses.sql['Password'],
                               db=tokens_and_addresses.sql['Database'])

        avg_from_home = '{}{}'.format('avg_', self.from_home_db_column)
        avg_to_home = '{}{}'.format('avg_', self.to_home_db_column)
        stdev_from_home = '{}{}'.format('stdev_', self.from_home_db_column)
        stdev_to_home = '{}{}'.format('stdev_', self.to_home_db_column)

        columns = ['day_code', 'hour', 'minute', avg_from_home, avg_to_home, stdev_from_home, stdev_to_home]

        df_mean_stdev = pd.DataFrame(columns=columns)

        if (day_code >= 0 and day_code <= 6):
            query = "select hour, minute, {}, {} from {} " \
                    "where day_code={} " \
                    "order by hour asc, minute asc " \
                    "limit {}".format(self.from_home_db_column, self.to_home_db_column, self.table, str(day_code), str(num_records))

        if (day_code == 8):
            query = "select hour, minute, {}, {} from {} " \
                        "where not (day_code=5 or day_code=6) " \
                        "order by hour asc, minute asc " \
                        "limit {}".format(self.from_home_db_column, self.to_home_db_column, self.table, str(num_records))

        elif (day_code == 9):
            query = "select hour, minute, {}, {} from {} " \
                        "where day_code=5 or day_code=6 " \
                        "order by hour asc, minute asc " \
                        "limit {}".format(self.from_home_db_column, self.to_home_db_column, self.table, str(num_records))

        commute_df = sql.read_sql(query, con=conn)
        start_time = time.time()

        for hour in range(0, 24):
            commute_df_hour = commute_df[commute_df.hour == hour]
            for minute in range(0, 41, 20):
                commute_df_hour_minute = commute_df_hour[
                    commute_df_hour['minute'].between(minute, minute + 20 - 1, inclusive=True)]
                if len(commute_df_hour_minute) > 0:
                    df_mean_stdev.loc[len(df_mean_stdev)] = [day_code, hour, minute,
                                                             commute_df_hour_minute[self.from_home_db_column].mean(),
                                                             commute_df_hour_minute[self.to_home_db_column].mean(),
                                                             commute_df_hour_minute[self.from_home_db_column].std(),
                                                             commute_df_hour_minute[self.to_home_db_column].std()]
                else:
                    continue

        self.drive_time_avg_from_home_list = df_mean_stdev[avg_from_home].tolist()
        self.drive_time_avg_to_home_list = df_mean_stdev[avg_to_home].tolist()
        self.drive_time_stdev_from_home_list = df_mean_stdev[stdev_from_home].tolist()
        self.drive_time_stdev_to_home_list = df_mean_stdev[stdev_to_home].tolist()

        date_list = []

        for row in df_mean_stdev.itertuples():
            hour = date_formatter(int(row.hour))
            minute = date_formatter(int(row.minute))
            date = '{}:{}'.format(hour, minute)
            date_list.append(date)

        self.date_list = date_list

        print('Total time: ', time.time() - start_time)

        conn.close()

    def get_commute_analysis(self, num_records):
        """
        Retrieves list of commute data for all days from database and computes average and standard deviation for each
        direction as well as rush hour date to and from home defined by morning rush hour between 6:00-10:00 and
        evening rush hour between 15:00-19:00.  Results are assigned to analysis_result_str_list and
        analysis_result_min_max_list.

        :param num_records: Number of database records to return
        :type num_records: int
        """

        conn = pymysql.connect(host=tokens_and_addresses.sql['Host'], port=tokens_and_addresses.sql['Port'],
                               user=tokens_and_addresses.sql['Username'], passwd=tokens_and_addresses.sql['Password'],
                               db=tokens_and_addresses.sql['Database'])

        query = "select hour, minute, day_code, {}, {} from {} " \
                "order by id desc limit {}".format(self.from_home_db_column, self.to_home_db_column, self.table, str(num_records))
        commute_df = sql.read_sql_query(query, con=conn)

        average_from_home_list = []
        stdev_from_home_list = []
        average_to_home_list = []
        stdev_to_home_list = []
        average_from_home_morning_rush_list = []
        stdev_from_home_morning_rush_list = []
        average_to_home_evening_rush_list = []
        stdev_to_home_evening_rush_list = []

        for day in range (0,7):
            commute_df_day = commute_df[commute_df.day_code == day]
            average_from_home_list.append(round(commute_df_day[self.from_home_db_column].mean(), 2))
            stdev_from_home_list.append(round(commute_df_day[self.from_home_db_column].std(), 2))
            average_to_home_list.append(round(commute_df_day[self.to_home_db_column].mean(), 2))
            stdev_to_home_list.append(round(commute_df_day[self.to_home_db_column].std(), 2))

            commute_df_from_home_morning_rush = commute_df_day[
                commute_df_day['hour'].between(6, 10, inclusive=True)]
            average_from_home_morning_rush_list.append(
                round(commute_df_from_home_morning_rush[self.from_home_db_column].mean(), 2))
            stdev_from_home_morning_rush_list.append(
                round(commute_df_from_home_morning_rush[self.from_home_db_column].std(), 2))

            commute_df_to_home_evening_rush = commute_df_day[
                commute_df_day['hour'].between(15, 19, inclusive=True)]
            average_to_home_evening_rush_list.append(
                round(commute_df_to_home_evening_rush[self.to_home_db_column].mean(), 2))
            stdev_to_home_evening_rush_list.append(
                round(commute_df_to_home_evening_rush[self.to_home_db_column].std(), 2))

        result_list_min_max=[]
        result_list_str = []
        result_list_float = [average_from_home_list, stdev_from_home_list, average_to_home_list, stdev_to_home_list,
                             average_from_home_morning_rush_list, stdev_from_home_morning_rush_list,
                             average_to_home_evening_rush_list, stdev_to_home_evening_rush_list]

        for i in range(len(result_list_float)):
            min = result_list_float[i][0]
            min_index = 0
            max = result_list_float[i][0]
            max_index = 0
            string_convert_list = []
            for j in range(len(result_list_float[i])):
                string_convert_list.append(str(result_list_float[i][j]))
            for j in range(len(result_list_float[i])-2):  # '-2' removed analysis from weekends
                if result_list_float[i][j] < min:
                    min = result_list_float[i][j]
                    min_index = j
                if result_list_float[i][j] > max:
                    max = result_list_float[i][j]
                    max_index = j

            result_list_str.append(string_convert_list)
            result_list_min_max.append([min_index, max_index])

        self.analysis_result_str_list = result_list_str
        self.analysis_result_min_max_list = result_list_min_max

def date_formatter(date_val):
    """
    Auto formats date values (month, day, hour, minute) to two digits.  This is needed for
    proper date formatting by Plotly.
    i.e. the month of March is represented in the database as and integer of 3.  This needs
    to be changed to a string of '03' to be plotted properly.

    :param date_val: Date/time value (month, day, hour, minute, second)
    :type date_val: int
    """
    if date_val < 10:
        date_val = '{}{}'.format('0', str(date_val))
        return date_val
    elif date_val >= 10:
        return str(date_val)
    else:
        print('Improper date value formatting')
        print(date_val)
