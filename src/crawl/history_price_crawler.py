from src.config.definitions import DOLLAR_TO_CNY
from src.config.urls import *
from src.util.requester import *
from src.util.logger import log


def crawl_item_history_price(index, item, total_price_number):
    history_prices = []

    item_id = item.id
    steam_price_url = steam_price_history_url(item)
    log.info('GET steam history price {}/{} for ({}): {}'.format(index, total_price_number, item.name, steam_price_url))
    steam_history_prices = get_json_dict(steam_price_url, steam_cookies, True)

    if steam_history_prices is not None:
        raw_price_history = steam_history_prices['prices']
        days = min(len(raw_price_history), 7)
        for pair in reversed(raw_price_history):
            if len(pair) == 3:
                history_prices.append(float(pair[1]))
            if len(history_prices) == days:
                break;

        # set history price if exist
        if len(history_prices) != 0:
            item.set_history_prices(history_prices, days)

        log.info('totally {} pieces of price history in {} days for {}\n'.format(len(history_prices), days, item.name))


def crawl_history_price(csgo_items):
    total_price_number = len(csgo_items)
    log.info('Total {} items to get history price.'.format(total_price_number))

    for index, item in enumerate(csgo_items, start=1):
        crawl_item_history_price(index, item, total_price_number)
