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


if __name__ == "__main__":
    main()
