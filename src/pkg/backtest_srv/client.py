"""src/pkg/backtest_srv/client.py\n
fetch_signal_data(ctx: dict) -> None
"""

import logging

# from pkg import DEBUG
# from pkg.backtest_srv import strategy, utils


# logger = logging.getLogger(__name__)


# def fetch_ohlc_data(ctx: dict) -> None:
#     """Data for OHLC price and volume."""
#     if DEBUG:
#         logger.debug(f"fetch_ohlc_data(ctx={ctx}")
#     if not DEBUG:
#         print(" Begin download process:")

#     # create database
#     utils.create_sqlite_ohlc_database(ctx=ctx)

#     # select data provider
#     processor = _select_data_provider(ctx=ctx)

#     # get and save data for each signal line
#     for ticker in ctx["interface"]["ticker"]:
#         if not DEBUG:
#             print(f"  - fetching {ticker}\t", end="")

#         data_tuple = processor.download_and_parse_price_data(ticker=ticker)
#         utils.write_price_volume_data_to_ohlc_table(ctx=ctx, data_tuple=data_tuple)

#     if not DEBUG:
#         print(" finished.")


# def fetch_signal_data(ctx: dict) -> None:
#     """Data for calculating indicators i.e. clv, price, volume etc."""
#     if DEBUG:
#         logger.debug(f"fetch_signal_data(ctx={ctx}")
#     if not DEBUG:
#         print(" Begin download process:")

#     # create database
#     utils.create_sqlite_signal_database(ctx=ctx)

#     # select data provider
#     processor = _select_data_provider(ctx=ctx)

#     # get and save data for each ticker
#     for ticker in ctx["interface"]["ticker"]:
#         if not DEBUG:
#             print(f"  - fetching {ticker}\t", end="")

#         data_tuple = processor.download_and_parse_price_data(ticker=ticker)
#         utils.write_data_line_to_signal_table(ctx=ctx, data_tuple=data_tuple)

#     if not DEBUG:
#         print(" finished.")


# def _select_data_provider(ctx: dict) -> object:
#     """Use provider from data service config file"""
#     if DEBUG:
#         logger.debug(f"_select_data_provider(ctx={type(ctx)})")

#     match ctx["data_service"]["data_provider"]:
#         case "tiingo":
#             from pkg.data_srv.agent import TiingoDataProcessor
#             return TiingoDataProcessor(ctx=ctx)
#         case "yfinance":
#             from pkg.data_srv.agent import YahooFinanceDataProcessor
#             return YahooFinanceDataProcessor(ctx=ctx)
#         case _:
#             raise ValueError(f"unknown provider: {ctx['data_service']['data_provider']}")
