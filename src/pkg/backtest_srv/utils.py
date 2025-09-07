"""src/pkg/data_srv/utils.py\n
create_sqlite_ohlc_database(ctx: dict) -> None\n
create_sqlite_signal_database(ctx: dict) -> None\n
write_data_line_to_stonk_table(ctx: dict, data_tuple: tuple) -> None"""

import logging

from pathlib import Path

from pkg import DEBUG
from pkg.ctx_mgr import SqliteConnectManager


logger = logging.getLogger(__name__)


def create_sqlite_ohlc_database(ctx: dict) -> None:
    """Create sqlite3 database. Table for each ticker symbol, column for OHLC, volume."""
    if DEBUG:
        logger.debug(f"create_sqlite_ohlc_database(ctx={ctx})")

    # create data folder in users work_dir
    Path(f"{ctx['default']['work_dir']}{ctx['interface']['command']}").mkdir(parents=True, exist_ok=True)
    # if old database exists remove it
    Path(f"{ctx['default']['work_dir']}{ctx['interface']['command']}/{ctx['interface']['database']}").unlink(
        missing_ok=True
    )

    try:
        with SqliteConnectManager(ctx=ctx, mode="rwc") as con:
            # create table for each ticker symbol
            for table in ctx["interface"]["ticker"]:
                # create ohlc table for ticker
                con.cursor.execute(
                    f"""
                    CREATE TABLE {table} (
                        datetime      INTEGER    NOT NULL,
                        open          INTEGER,
                        high          INTEGER,
                        low           INTEGER,
                        close         INTEGER,
                        volume        INTEGER,
                        PRIMARY KEY (datetime)
                    )"""
                )
    except con.sqlite3.Error as e:
        logger.debug(f"*** ERROR *** {e}")

    if not DEBUG:
        print(f"\n Created db: '{con.db_path}'")


def create_sqlite_signal_database(ctx: dict) -> None:
    """Create sqlite3 database. Table for each ticker symbol, column for each data line."""
    if DEBUG:
        logger.debug(f"create_sqlite_signal_database(ctx={type(ctx)})")

    # create data folder in users work_dir
    Path(f"{ctx['default']['work_dir']}{ctx['interface']['command']}").mkdir(parents=True, exist_ok=True)
    # if old database exists remove it
    Path(f"{ctx['default']['work_dir']}{ctx['interface']['command']}/{ctx['interface']['database']}").unlink(
        missing_ok=True
    )

    try:
        with SqliteConnectManager(ctx=ctx, mode="rwc") as con:
            # create table for each ticker symbol
            for table in ctx["interface"]["ticker"]:
                con.cursor.execute(
                    f"""
                    CREATE TABLE {table.upper()} (
                        datetime    INTEGER    NOT NULL,
                        PRIMARY KEY (datetime)
                    )
                """
                )
                # add column for each indicator (data_line)
                for col in ctx["interface"]["signal_line"]:
                    con.cursor.execute(
                        f"""
                        ALTER TABLE {table} ADD COLUMN {col.lower()} INTEGER
                    """
                    )
    except con.sqlite3.Error as e:
        logger.debug(f"*** ERROR *** {e}")

    if not DEBUG:
        print(f"\n Created db: '{con.db_path}'")


def write_price_volume_data_to_ohlc_table(ctx: dict, data_tuple: tuple) -> None:
    """"""
    if DEBUG:
        logger.debug(
            f"write_price_volume_data_to_ohlc_table(ctx={ctx}, data_tuple[0]: {data_tuple[0]}, data_tuple[1]:\n{data_tuple[1]})"
        )
    ohlc_table = data_tuple[0]
    data_list = list(data_tuple[1].itertuples(index=True, name=None))

    if not DEBUG:
        print(f"writing {ohlc_table} to db...")

    try:
        with SqliteConnectManager(ctx=ctx, mode="rw") as con:
            if DEBUG:
                logger.debug(f"ohlc_table: {ohlc_table}, data_list: {data_list}, {type(data_list)}")
            con.cursor.executemany(f"INSERT INTO {ohlc_table} VALUES (?,?,?,?,?,?)", data_list)
    except con.sqlite3.Error as e:
        logger.debug(f"*** Error *** {e}")


def write_data_line_to_signal_table(ctx: dict, data_tuple: tuple) -> None:
    """"""
    if DEBUG:
        logger.debug(
            f"write_data_line_to_stonk_table(ctx={ctx}, data_tuple[0]: {data_tuple[0]}, data_tuple[1]:\n{data_tuple[1]})"
        )
    signal_table = data_tuple[0]
    data_list = list(data_tuple[1].itertuples(index=True, name=None))

    if not DEBUG:
        print(f"writing {signal_table} to db...")

    try:
        with SqliteConnectManager(ctx=ctx, mode="rw") as con:
            if DEBUG:
                logger.debug(f"signal_table: {signal_table}, data_list: {data_list}, {type(data_list)}")
            # con.cursor.executemany(f"INSERT INTO {signal_table} VALUES (?,?,?)", data_list)
            con.cursor.executemany(f"INSERT INTO {signal_table} VALUES (?,?,?,?,?,?)", data_list)
    except con.sqlite3.Error as e:
        logger.debug(f"*** Error *** {e}")
