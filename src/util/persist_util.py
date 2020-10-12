import os

import pandas as pd

from src.util import converter
from src.util.logger import log


def tabulate(csgo_items):
    if len(csgo_items) != 0:
        # persist data
        table = converter.list_to_df(csgo_items)
        table_info(table)

        return table
    else:
        return None


def table_info(table):
    log.info(table)
    log.info(table.describe())
    log.info('\n')