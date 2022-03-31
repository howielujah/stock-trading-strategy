import pandas as pd
import requests
import time
import re
from bs4 import BeautifulSoup
from trading_calendars import get_calendar


def retry_requests(url, payloads, headers):

    for i in range(3):
        try:
            return requests.get(url, params=payloads, headers=headers)
        except:
            print('An error occurred, try after 1 minute')
            time.sleep(60)

    return None


def get_codes(url):

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.80 Safari/537.36'
    }

    response = retry_requests(url, None, headers)
    result = []
    try:
        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.find_all(href=re.compile("^javascript:Link2Stk\('"))
        for link in links:
            result.append(link.getText().split()[0])
    except:
        print('No information found')
    return result


def get_daily_prices(date, connection):

    try:
        df = pd.read_sql("select * from daily_prices where 日期 = '{}'".format(date),
                         connection,
                         parse_dates=['日期'],
                         index_col=['證券代號', '日期'])
    except:
        df = pd.DataFrame()

    if not df.empty:
        return df, True

    url = 'https://www.twse.com.tw/exchangeReport/MI_INDEX'

    payloads = {
        'response': 'html',
        'date': date.strftime('%Y%m%d'),
        'type': 'ALLBUT0999'
    }

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.80 Safari/537.36'
    }

    response = retry_requests(url, payloads, headers)

    try:
        df = pd.read_html(response.text)[-1]
    except Exception as e:
        print('{} {}'.format(date.strftime('%Y%m%d'), e))
        return None, False

    df.columns = df.columns.get_level_values(2)

    df['漲跌價差'] = df['漲跌價差'].where(df['漲跌(+/-)'] != '-', - df['漲跌價差'])

    df.drop(['證券名稱', '漲跌(+/-)'], inplace=True, axis=1)

    df['日期'] = pd.to_datetime(date)

    df = df.set_index(['證券代號', '日期'])

    df = df.apply(pd.to_numeric, errors='coerce')

    df.drop(df[df['收盤價'].isnull()].index, inplace=True)

    df['昨日收盤價'] = df['收盤價'] - df['漲跌價差']

    df['股價振幅'] = (df['最高價'] - df['最低價']) / df['昨日收盤價'] * 100

    return df, False


def update_daily_prices(start_date, end_date, connection):

    tw_calendar = get_calendar('XTAI')

    main_df = pd.DataFrame()

    for date in pd.date_range(start_date, end_date):

        if date not in tw_calendar.opens:
            continue

        df, in_db = get_daily_prices(date, connection)

        if df is not None and not in_db:
            main_df = main_df.append(df, sort=False)
            print('{} The daily closing quotation is captured, wait for 15 seconds'.format(
                date.strftime('%Y%m%d')))
            time.sleep(15)

    if not main_df.empty:
        main_df.to_sql('daily_prices', connection, if_exists='append')
        return main_df


def update_historical_data(start_date, end_date, connection):

    tw_calendar = get_calendar('XTAI')

    start = pd.to_datetime(start_date)
    end = pd.to_datetime(end_date)

    print('Updating daily closing quotes...')

    update_daily_prices(tw_calendar.previous_close(
        start).date(), end, connection)
