import sqlite3
import sys
from datetime import datetime, timedelta
from database import *


def main():
    # Find stocks held by both foreign investors and investment trusts
    foreign_purchases = get_codes(
        'https://fubon-ebrokerdj.fbs.com.tw/Z/ZG/ZG_D.djhtm')
    investment_trust_purchases = get_codes(
        'https://fubon-ebrokerdj.fbs.com.tw/Z/ZG/ZG_DD.djhtm')
    list = []
    for purchase in foreign_purchases:
        if purchase in investment_trust_purchases:
            list.append(purchase)
    print(list)
    start_date = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] else (
        datetime.now() - timedelta(1)).strftime("%Y/%-m/%-d")
    end_date = sys.argv[2] if len(
        sys.argv) > 2 and sys.argv[2] else datetime.now().strftime("%Y/%-m/%-d")
    connection = sqlite3.connect('data.db')
    update_historical_data(start_date, end_date, connection)


if __name__ == "__main__":
    main()
