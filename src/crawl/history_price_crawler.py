from asyncio.tasks import gather
import traceback
import asyncio
from datetime import datetime

import aiohttp

from src.config.urls import steam_price_history_url
from src.util.logger import log
from src.util.requester import async_get_json_dict, get_headers, steam_cookies, get_json_dict


async def crawl_item_history_price(index, item, total_price_number, session):
    history_prices = []

    steam_price_url = steam_price_history_url(item)
    log.info('prepare to GET steam history price {}/{} for ({}): {}'.format(index, total_price_number, item.name, steam_price_url))

    # 通过注释切换同步/异步爬取：（同步爬取下引入mode降低了steam market的爬取间隔）
    # steam_history_prices = get_json_dict(steam_price_url, steam_cookies, session, True, mode = 1)
    steam_history_prices = await async_get_json_dict(steam_price_url, steam_cookies, session, True)

    # key existence check
    if (steam_history_prices is not None) and ('prices' in steam_history_prices):
        raw_price_history = steam_history_prices['prices']
        if len(raw_price_history) > 0:
            days = min((datetime.today().date() - datetime.strptime(raw_price_history[0][0], '%b %d %Y %H: +0').date()).days, 7)
        else:
            days = 0
        for pair in reversed(raw_price_history):
            if len(pair) == 3:
                for i in range(0, int(pair[2])):
                    history_prices.append(float(pair[1]))
            if (datetime.today().date() - datetime.strptime(pair[0], '%b %d %Y %H: +0').date()).days > days:
                break

        # set history price if exist
        if len(history_prices) != 0:
            item.set_history_prices(history_prices, days)

        log.info('got steam history price {}/{} for ({}): {}'.format(index, total_price_number, item.name, steam_price_url))
        log.info('totally {} pieces of price history in {} days for {}\n'.format(len(history_prices), days, item.name))


async def crawl_history_price(csgo_items):
    total_price_number = len(csgo_items)
    log.info('Total {} items to get history price.'.format(total_price_number))

    tasks = []
    async with aiohttp.ClientSession(cookies=steam_cookies, headers=get_headers(), connector = aiohttp.TCPConnector(limit=5)) as session:
        for index, item in enumerate(csgo_items, start=1):
            try:
                tasks.append(
                    crawl_item_history_price(index, item, total_price_number, session))
            except Exception as e:
                log.error(traceback.format_exc())
            # 每次执行100个任务：
            if len(tasks) > 100:
                try:
                    await asyncio.gather(*tasks)
                except Exception as e:
                    log.error(traceback.format_exc())
                tasks = []
        try:
            await asyncio.gather(*tasks)
        except Exception as e:
            log.error(traceback.format_exc())
