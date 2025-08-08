""""""
import datetime
import logging, logging.config
import os, pickle

from statistics import fmean

import pandas as pd

from dotenv import load_dotenv
from numpy.lib.stride_tricks import sliding_window_view
from sklearn.preprocessing import RobustScaler


DEBUG = True
load_dotenv()

logging.config.fileConfig(fname="src/logger.ini")
logging.getLogger("peewee").setLevel(logging.WARNING)
logging.getLogger("yfinance").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

ctx = {
    'default': {
        'debug': True,
        'indicator': 'AFK ASEA ECNS EZU FXI HYG XLF XLY',
        'target': 'SPXL SPXS YINN YANG',
        'work_dir': '/home/la/dev/rl/stonk_cli/work_dir/',
        'cfg_chart': '/home/la/dev/rl/stonk_cli/src/pkg/chart_srv/cfg_chart.ini',
        'cfg_data': '/home/la/dev/rl/stonk_cli/src/pkg/data_srv/cfg_data.ini',
        'cfg_main': '/home/la/dev/rl/stonk_cli/src/config.ini'
    },
    'interface': {
        'command': 'data',
        'database': 'default.db',
        'data_line': ['CWAP', 'VOLUME'],
        # 'ticker': ['AFK', 'ASEA', 'ECNS', 'EZU', 'FXI', 'HYG', 'SPXL', 'SPXS', 'XLF', 'XLY', 'YANG', 'YINN'],
        # 'ticker': ['YANG', 'YINN'],
        'ticker': ['SPXS'],
        'window_size': 3,
    },
    'chart_service': {
        'adblock': '',
        'heatmap_list': '1W 1M 3M 6M',
        'url_stockchart': 'https://stockcharts.com/sc3/ui/?s=AAPL',
        'url_heatmap': 'https://stockanalysis.com/markets/heatmap/',
        'webdriver': 'geckodriver'
    },
    'data_service': {
        'data_frequency': 'daily',
        'data_line': 'CWAP VOLUME',
        'data_lookback': '21',
        # 'data_lookback': '2646',
        'data_provider': 'yfinance',
        'sklearn_scaler': 'RobustScaler',
        'url_alphavantage': 'https://www.alphavantage.co/query',
        'url_tiingo': '',
        'url_yfinance': '',
        'token_alphavantage': os.getenv('TOKEN_ALPHAVANTAGE'),
        'token_alphavantage_1': os.getenv('TOKEN_ALPHAVANTAGE_1'),
        'token_tiingo': os.getenv('TOKEN_TIINGO'),
        'window_size': 3,
    }
}


class BaseProcessor:
    """"""
    def __init__(self, ctx: dict):
        self.data_line = ctx["interface"]["data_line"]
        self.data_provider = ctx["data_service"]["data_provider"]
        self.frequency = ctx["data_service"]["data_frequency"]
        self.index = None
        self.lookback = int(ctx["data_service"]["data_lookback"])
        self.scaler = self._set_sklearn_scaler(ctx["data_service"]["sklearn_scaler"])
        self.start_date, self.end_date = self._start_end_date
        self.window_size = int(ctx['interface']['window_size'])
        self.work_dir = ctx["default"]["work_dir"]

    @property
    def _start_end_date(self):
        """Set the start and end dates"""
        lookback = int(self.lookback)
        start = datetime.date.today() - datetime.timedelta(days=lookback)
        end = datetime.date.today()
        return start, end

    def _set_sklearn_scaler(self, scaler):
        """Uses config file [data_service][sklearn_scaler] value"""
        if scaler == "MinMaxScaler":
            from sklearn.preprocessing import MinMaxScaler
            return MinMaxScaler()
        elif scaler == "RobustScaler":
            from sklearn.preprocessing import RobustScaler
            # return RobustScaler(quantile_range=(0.0, 100.0))
            return RobustScaler()

    def _sliding_window_scaled_data(self, data_list: list):
        """"""
        if DEBUG: logger.debug(f"_sliding_window_scaled_data(data_list={data_list})")

        scaled_data = list()
        v = sliding_window_view(x=data_list, window_shape=self.window_size)

        # scale each row in window view then append last item to scaled_data list
        for row in v:
            scaled_row = self.scaler.fit_transform(X=row.reshape(-1, 1))
            scaled_item = int((scaled_row.item(-1) + 10) * 100)
            scaled_data.append(scaled_item)

        # pad front of scaled_data with average value
        return [int(fmean(scaled_data))] * (self.window_size - 1) + scaled_data

    def download_and_parse_price_data(self, ticker: str) -> tuple:
        """Returns a tuple, (ticker, dataframe)"""
        if DEBUG:
            logger.debug(f"download_and_parse_price_data(self={self}, ticker={ticker})")

        if not DEBUG:
            print(f"  - fetching {ticker}...\t", end="")
        data_gen = eval(f"self._{self.data_provider}_data_generator(ticker=ticker)")

        return eval(f"self._process_{self.data_provider}_data(data_gen=data_gen)")


class YahooFinanceDataProcessor(BaseProcessor):
    """Fetch ohlc price data using yfinance"""

    import yfinance as yf

    def __init__(self, ctx: dict):
        super().__init__(ctx=ctx)
        self.interval = self._parse_frequency

    def __repr__(self):
        return (
            f"{self.__class__.__name__}("
            f"data_line={self.data_line}, "
            f"data_provider={self.data_provider}, "
            f"interval={self.interval}, "
            f"scaler={self.scaler}, "
            f"start_date={self.start_date}, "
            f"end_date={self.end_date})"
        )

    @property
    def _parse_frequency(self):
        """Convert daily/weekly frequency to provider format"""
        frequency_dict = {"daily": "1d", "weekly": "1w"}
        return frequency_dict[self.frequency]

    def _yfinance_data_generator(self, ticker: str) -> object:
        """Yields a generator object tuple (ticker, dataframe)"""
        if DEBUG:
            logger.debug(f"_yfinance_data_generator(ticker={ticker})")
        # try:
        #     yf_data = self.yf.Ticker(ticker=ticker)
        #     yf_df = yf_data.history(start=self.start_date, end=self.end_date, interval=self.interval)
        # except Exception as e:
        #     logger.debug(f"*** ERROR *** {e}")
        # else:
        #     with open(f"{ctx['default']['work_dir']}{ticker}.pkl", "wb") as pkl:
        #         pickle.dump((ticker, yf_df), pkl)
        #     yield ticker, yf_df

        # yield data from saved pickle
        with open(f"{ctx['default']['work_dir']}{ticker}.pkl", "rb") as pkl:
            ticker, df = pickle.load((pkl))
        yield ticker, df


    def _process_yfinance_data(self, data_gen: object) -> pd.DataFrame:
        """Returns a tuple (ticker, dataframe)"""
        if DEBUG:
            logger.debug(f"_process_yfinance_data(data_gen={type(data_gen)})")

        ticker, yf_df = next(data_gen)
        yf_df = yf_df.drop(columns=yf_df.columns.values[-3:], axis=1)

        # create empty dataframe with index as a timestamp
        index = yf_df.index.values.astype(int) // 10**9
        df = pd.DataFrame(index=index)
        df.index.name = "date"

        # close weighted average price exclude open price
        cwap = list(round(
            (2 * yf_df["Close"] + yf_df["High"] + yf_df["Low"]) * 25
        ).astype(int))
        if DEBUG: logger.debug(f"cwap array: {cwap} {type(cwap)}")

        cwap = self._sliding_window_scaled_data(data_list=cwap)
        if DEBUG: logger.debug(f"scaled cwap: {cwap} {type(cwap)} len {len(cwap)}")

        # number of shares traded
        volume = list(yf_df["Volume"])
        if DEBUG: logger.debug(f"volume array: {volume} {type(volume)}")

        volume = self._sliding_window_scaled_data(data_list=volume)
        if DEBUG: logger.debug(f"scaled volume: {volume} {type(volume)} len {len(volume)}")

        # insert values for each data line into df
        for i, item in enumerate(self.data_line):
            df.insert(loc=i, column=f"{item.lower()}", value=eval(item.lower()), allow_duplicates=True)

        return ticker, df


def main(ctx: dict):
    if DEBUG:
        logger.debug(f"main(ctx={type(ctx)})")

    def sliding_window_scaled_data(data_list: list, window_size: int):
        """"""
        if DEBUG:
            logger.debug(f"sliding_window_scaled_data(data_list={data_list}, window_size={window_size})")

        v = sliding_window_view(x=data_list, window_shape=window_size)
        scaler = RobustScaler()
        scaled_data = list()

        # scale each row in window view then append last item to scaled_data list
        for row in v:
            scaled_row = scaler.fit_transform(X=row.reshape(-1, 1))
            scaled_item = int((scaled_row.item(-1) + 10) * 100)
            scaled_data.append(scaled_item)

        # pad front of scaled_data with average value
        return [int(fmean(scaled_data))] * (window_size - 1) + scaled_data

    # get data from saved pickle
    with open(f"{ctx['default']['work_dir']}SPXS.pkl", "rb") as pkl:
        ticker, yf_df = pickle.load((pkl))

    yf_df = yf_df.drop(columns=yf_df.columns.values[-3:], axis=1)
    if DEBUG: logger.debug(f"ticker: {ticker}, dataframe:\n{yf_df}")

    # close weighted average price exclude open price
    cwap = list(round(
        (2 * yf_df["Close"] + yf_df["High"] + yf_df["Low"]) * 25
    ).astype(int))
    if DEBUG: logger.debug(f"cwap array: {cwap} {type(cwap)}")

    cwap = sliding_window_scaled_data(data_list=cwap, window_size=ctx['interface']['window_size'])
    if DEBUG: logger.debug(f"scaled cwap: {cwap} {type(cwap)} len {len(cwap)}")

    # number of shares traded
    volume = list(yf_df["Volume"])
    if DEBUG: logger.debug(f"volume array: {volume} {type(volume)}")

    volume = sliding_window_scaled_data(data_list=volume, window_size=ctx['interface']['window_size'])
    if DEBUG: logger.debug(f"scaled volume: {volume} {type(volume)} len {len(volume)}")

    # create empty dataframe with index as a timestamp
    index = yf_df.index.values.astype(int) // 10**9
    df = pd.DataFrame(index=index)
    df.index.name = "date"

    # # insert values for each data line into df
    for i, item in enumerate(['CWAP', 'VOLUME']):
        df.insert(loc=i, column=f"{item.lower()}", value=eval(item.lower()), allow_duplicates=True)

    if DEBUG: logger.debug(f"ticker: {ticker}, dataframe:\n{df}")

# =======

    # create database
    # utils.create_sqlite_indicator_database(ctx=ctx)

    # select data provider
    processor = YahooFinanceDataProcessor(ctx=ctx)

    for index, ticker in enumerate(ctx['interface']['ticker']):
        ctx['interface']['index'] = index  # alphavantage may throttle at five downloads
        data_tuple = processor.download_and_parse_price_data(ticker=ticker)
        if DEBUG: logger.debug(f"ticker: {data_tuple[0]}, dataframe:\n{data_tuple[1]}")

        # utils.write_indicator_data_to_sqlite_db(ctx=ctx, data_tuple=data_tuple)


if __name__ == "__main__":
    if DEBUG:
        logger.debug(f"******* START - stonk_cli/beta_data_line.py.main() *******")
    main(ctx=ctx)
