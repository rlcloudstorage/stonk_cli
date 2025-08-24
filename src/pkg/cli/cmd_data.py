"""src/pkg/cli/cmd_data.py"""

import logging

import click

from pkg import DEBUG
from pkg.data_srv import client


logger = logging.getLogger(__name__)


@click.command(
    "data",
    short_help="Fetch online stockmarket data",
    help="""
\b
NAME
    data - Fetch online stockmarket data
\b
DESCRIPTION
    The data utility fetches historical ohlc stock price data.
    Downloaded data is saved to the work directory. If no ticker
    symbols (arguments) are provided the default symbol list is used.
    If no option is given signal data are downloaded.
""",
)
@click.argument("arguments", nargs=-1, default=None, required=False, type=str)
@click.option("-o", "--ohlc", "opt_trans", flag_value="ohlc", help="Fetch OHLC price and volume data.")
@click.option("-s", "--signal", "opt_trans", flag_value="signal", help="Fetch data line (signal) data.")

# @click.pass_context
@click.pass_obj
def cli(ctx, arguments, opt_trans):
    """Run data command"""
    if DEBUG:
        logger.debug(f"start_cli(ctx={type(ctx)}, arguments={arguments}, opt_trans={opt_trans})")

    ctx["interface"]["command"] = "data"

    # set data_list and client method based on opt_trans value
    match opt_trans:
        case "False" | "signal":
            ctx["interface"]["client"] = "signal"
            data_list = "signal_tic_list"
            database = "signal.db"
        case "ohlc":
            ctx["interface"]["client"] = "ohlc"
            data_list = "ohlc_tic_list"
            database = "ohlc.db"

    # add arguments to interface ctx and set database name
    if arguments:
        # use symbols in arguments list
        ticker_list = sorted([i.upper() for i in list(arguments)])
        ctx["interface"]["database"] = click.prompt(
            f"* Using database 'custom_{database}'. Type a new database name to change,\n  press Enter to accept.",
            default=f"custom_{database}",
        )
    else:
        # use symbols from default ticker list
        if ctx["data_service"][data_list]:
            ticker_list = sorted(list(ctx["data_service"][data_list].split(" ")))
        else:
            try:
                ticker_list = sorted(list(ctx["default"][data_list].split(" ")))
            except:
                click.echo(message="Add tickers to data_list in data_service/cfg_data.ini file.")

        ctx["interface"]["database"] = click.prompt(
            f"* Using database 'default_{database}'. Type a new database name to change,\n  press Enter to accept",
            default=f"default_{database}",
        )
    ctx["interface"]["ticker"] = ticker_list


    if ctx["interface"]["client"] == "signal":
        # show signal cli prompt info
        signal_line = click.prompt(
            f"* Using signal line '{ctx['data_service']['signal_line']}'. Type a new value to change,\n  press Enter to accept",
            default=ctx["data_service"]["signal_line"],
        )
        ctx["interface"]["signal_line"] = sorted([i.upper() for i in signal_line.split(" ")])

        ctx["interface"]["window_size"] = click.prompt(
            f"* Using sliding window size {ctx['data_service']['window_size']}. Type a new value to change,\n  press Enter to accept",
            default=ctx["data_service"]["window_size"],
        )

    if ctx["interface"]["client"] == "ohlc":
        ctx["interface"]["signal_line"] = None
        ctx["interface"]["window_size"] = 0
        if click.confirm(f"* Saving {ctx['interface']['ticker']} OHLC data to '{ctx['interface']['database']}.\n  Do you want to continue?"):
            client.fetch_ohlc_data(ctx=ctx)

    elif ctx["interface"]["client"] == "signal":
        if click.confirm(f"* Saving signal line {ctx['interface']['signal_line']} for {ctx['interface']['ticker']} to '{ctx['interface']['database']}.\n  Do you want to continue?"):
            client.fetch_signal_data(ctx=ctx)

    if not DEBUG:
        print(
            f" Saved data to '{ctx['default']['work_dir']}{ctx['interface']['command']}/{ctx['interface']['database']}'\n"
        )
