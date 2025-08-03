""""""
import datetime
import logging, logging.config
import os, pickle

import numpy as np
import pandas as pd


DEBUG = True

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
        # 'ticker': ['AFK', 'ASEA', 'ECNS', 'EZU', 'FXI', 'HYG', 'SPXL', 'SPXS', 'XLF', 'XLY', 'YANG', 'YINN'],
        'ticker': ['YANG', 'YINN'],
        'data_line': ['CWAP', 'VOLUME']
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
        # 'data_lookback': '21',
        'data_lookback': '21',
        'data_provider': 'yfinance',
        'sklearn_scaler': 'MinMaxScaler',
        'url_alphavantage': 'https://www.alphavantage.co/query',
        'url_tiingo': '',
        'url_yfinance': '',
        'token_alphavantage': 'KLR0OYI8EAP1WSUU',
        'token_alphavantage_1': '75BLTZSVMHR16563',
        'token_tiingo': '75a0aa12dd1e297d613cfe92ecfe96dab95a4589'
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
            return RobustScaler(quantile_range=(0.0, 100.0))

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
        #     yield ticker, yf_df
        #     with open(f"{ctx['default']['work_dir']}{ticker}.pkl", "wb") as pkl:
        #         pickle.dump((ticker, yf_df), pkl)

        # yield data from saved pickle
        with open(f"{ctx['default']['work_dir']}{ticker}.pkl", "rb") as pkl:
            ticker, df = pickle.load((pkl))
        if DEBUG: logger.debug(f"ticker: {ticker}, dataframe:\n{df}")

        yield ticker, df


    def _process_yfinance_data(self, data_gen: object) -> pd.DataFrame:
        """Returns a tuple (ticker, dataframe)"""
        if DEBUG:
            logger.debug(f"_process_yfinance_data(data_gen={type(data_gen)})")

        ticker, yf_df = next(data_gen)
        yf_df = yf_df.drop(columns=yf_df.columns.values[-3:], axis=1)

        # create empty dataframe with index as a timestamp
        df = pd.DataFrame(index=yf_df.index.values.astype(int) // 10**9)
        df.index.name = "date"

        # close weighted average price exclude open price
        cwap = np.array(
            list((2 * yf_df["Close"] + yf_df["High"] + yf_df["Low"]) / 4)
        ).reshape(-1, 1)
        # cwap = np.rint((self.scaler.fit_transform(cwap).flatten() + 10) * 100).astype(int)
        cwap = np.rint((
            self.scaler.fit_transform(cwap).flatten() + 10
        ) * 100).astype(int)
        if DEBUG: logger.debug(f"scaled_cwap: {cwap} {type(cwap)}")

        # number of shares traded
        volume = np.array(list(yf_df["Volume"])).reshape(-1, 1)
        volume = np.rint((self.scaler.fit_transform(volume).flatten() + 10) * 100).astype(int)
        if DEBUG: logger.debug(f"scaled_volume: {volume} {type(volume)}")

        # insert values for each data line into df
        for i, item in enumerate(self.data_line):
            df.insert(loc=i, column=f"{item.lower()}", value=eval(item.lower()), allow_duplicates=True)

        return ticker, df


def main(ctx: dict):
    if DEBUG:
        logger.debug(f"main(ctx={ctx})")

    processor = YahooFinanceDataProcessor(ctx=ctx)

    for index, ticker in enumerate(ctx['interface']['ticker']):
        ctx['interface']['index'] = index  # alphavantage may throttle at five downloads
        data_tuple = processor.download_and_parse_price_data(ticker=ticker)
        if DEBUG:
            logger.debug(f"data_tuple: {data_tuple}, {type(data_tuple)}")


if __name__ == "__main__":
    if DEBUG:
        logger.debug(f"******* START - stonk_cli/beta_data_line.py.main() *******")
    main(ctx=ctx)
