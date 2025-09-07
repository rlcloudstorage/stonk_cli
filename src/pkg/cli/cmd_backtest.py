"""src/pkg/cli/cmd_backtest.py"""

import logging

from os import path

import click

from pkg import DEBUG
from pkg.backtest_srv import client


logger = logging.getLogger(__name__)


@click.command(
    "backtest",
    options_metavar='[plot] [OPTION]',
    short_help="Backtest trading strategy",
    help="""
\b
NAME
    backtest - Backtest stockmarket trading strategy
\b
DESCRIPTION
    Run backtest on a saved strategy against historical data from the
    stock OHLC database. Optional 'plot' can be specified as the first
    argument if plotting the backtest output is desired. File locations
    for database and strategy must exist in users work directory.
"""
)
@click.argument(
    "argument", nargs=-1, default=None, required=False, type=str
)
@click.option(
    "-db", "--database", "opt_trans",
    default=None,
    type=click.STRING,
    nargs=1,
    expose_value=True,
    flag_value="database",
    multiple=True,
    help="Set database used for backtesting.",
)
@click.option(
    "-s", "--strategy", "opt_trans",
    flag_value="strategy",
    multiple=True,
    help="Strategy to use for backtesting."
)

# @click.pass_context
@click.pass_obj
def cli(ctx, argument, opt_trans):
    """Run backtest command"""
    if DEBUG:
        logger.debug(f"start_cli(ctx={type(ctx)}, arguments={argument}, opt_trans={opt_trans})")

    ctx["interface"]["command"] = "backtest"
    ctx["interface"]["plot"] = False

    ctx["interface"]["argument"] = argument
    ctx["interface"]["opt_trans"] = opt_trans

    database = ctx['backtest_service']['database']
    strategy = ctx['backtest_service']['strategy']

    if not argument:
        database = ctx['backtest_service']['database']
        strategy = ctx['backtest_service']['strategy']
    else:
        for i in argument:
            if i in ["plot", "plt"]:
                ctx["interface"]["plot"] = True
                break

    for i in opt_trans:
        print(f" opt_trans: {i}")
        match i:
            case "database":
                # if not path.isfile(f""):
                #     click.echo(f"run stonk_cli data")
                print(f"*** {i} ***")
                try:
                    pass
                except:
                    pass
            case "strategy":
                print(f"*** {i} ***")
                try:
                    pass
                except:
                    pass
            case None:
                print(f"*** {i} ***")


    ctx["interface"]["database"] = database
    ctx["interface"]["strategy"] = strategy

    # if opt_trans == "database":
    #     if not argument:
    #         click.echo(f" Using default database: {ctx['backtest_service']['database']}")
    #         ctx["interface"]["database"] = ctx['backtest_service']['database']
    #     else:
    #         ctx["interface"]["database"] = utils.get_option_value(ctx=ctx)

    # if opt_trans == "strategy":
    #     if not argument:
    #         click.echo(f" Using default strategy: {ctx['backtest_service']['strategy']}")
    #         ctx["interface"]["strategy"] = ctx['backtest_service']['strategy']
    #     else:
    #         ctx["interface"]["strategy"] = utils.get_option_value(ctx=ctx)

    if DEBUG:
        logger.debug(f"cli(ctx={ctx})")

    # if click.confirm(f" Downloading: {ctx['interface']['arguments']}\n Do you want to continue?"):
    #     # Download heatmaps
    #     from pkg.chart_srv import client

    #     client.begin_chart_download(ctx)
    # else:  # Print default message
    #     click.echo("Goodby.")

    # # set data_list and client method based on opt_trans value
    # match opt_trans:
    #     case "False" | "signal":
    #         ctx["interface"]["client"] = "signal"
    #         data_list = "signal_tic_list"
    #         database = f"{ctx['data_service']['data_provider']}_{ctx['interface']['client']}.db"
    #     case "ohlc":
    #         ctx["interface"]["client"] = "ohlc"
    #         data_list = "ohlc_tic_list"
    #         database = f"{ctx['data_service']['data_provider']}_{ctx['interface']['client']}.db"

    # # add arguments to interface ctx and set database name
    # if arguments:
    #     # use symbols in arguments list
    #     ticker_list = sorted([i.upper() for i in list(arguments)])
    #     ctx["interface"]["database"] = click.prompt(
    #         f"* Using database 'custom_{database}'. Type a new database name to change,\n  press Enter to accept.",
    #         default=f"custom_{database}",
    #     )
    # else:
    #     # use symbols from default ticker list
    #     if ctx["data_service"][data_list]:
    #         ticker_list = sorted(list(ctx["data_service"][data_list].split(" ")))
    #     else:
    #         try:
    #             ticker_list = sorted(list(ctx["default"][data_list].split(" ")))
    #         except:
    #             click.echo(message="Add tickers to data_list in data_service/cfg_data.ini file.")

    #     ctx["interface"]["database"] = click.prompt(
    #         f"* Using database 'default_{database}'. Type a new database name to change,\n  press Enter to accept",
    #         default=f"{database}",
    #     )
    # ctx["interface"]["ticker"] = ticker_list


    # if ctx["interface"]["client"] == "signal":
    #     # show signal cli prompt info
    #     signal_line = click.prompt(
    #         f"* Using signal line '{ctx['data_service']['signal_line']}'. Type a new value to change,\n  press Enter to accept",
    #         default=ctx["data_service"]["signal_line"],
    #     )
    #     ctx["interface"]["signal_line"] = sorted([i.upper() for i in signal_line.split(" ")])

    #     ctx["interface"]["window_size"] = click.prompt(
    #         f"* Using sliding window size {ctx['data_service']['window_size']}. Type a new value to change,\n  press Enter to accept",
    #         default=ctx["data_service"]["window_size"],
    #     )

    # if ctx["interface"]["client"] == "ohlc":
    #     ctx["interface"]["signal_line"] = None
    #     ctx["interface"]["window_size"] = 0
    #     if click.confirm(f"* Saving {ctx['interface']['ticker']} OHLC data to '{ctx['interface']['database']}.\n  Do you want to continue?"):
    #         client.fetch_ohlc_data(ctx=ctx)

    # elif ctx["interface"]["client"] == "signal":
    #     if click.confirm(f"* Saving signal line {ctx['interface']['signal_line']} for {ctx['interface']['ticker']} to '{ctx['interface']['database']}.\n  Do you want to continue?"):
    #         client.fetch_signal_data(ctx=ctx)

    # if not DEBUG:
    #     print(
    #         f" Saved data to '{ctx['default']['work_dir']}{ctx['interface']['command']}/{ctx['interface']['database']}'\n"
    #     )

# =======

# @click.argument("arguments", nargs=-1, default=None, required=False, type=str)

# # @click.pass_context
# @click.pass_obj
# def cli(ctx, arguments):
#     """Run heatmap command"""
#     if DEBUG:
#         logger.debug(f"start_cli(ctx={type(ctx)}, arguments={arguments})")
#     ctx["interface"]["command"] = "heatmap"

#     # Add 'arguments' to 'interface' ctx
#     if arguments:  # download heatmaps in arguments list
#         ctx["interface"]["arguments"] = sorted([a.upper() for a in list(arguments)])
#     else:  # use chart_service heat_map list
#         ctx["interface"]["arguments"] = sorted(list(ctx["chart_service"]["heatmap_list"].split(" ")))

#     if DEBUG:
#         logger.debug(f"cli(ctx={ctx})")

#     if click.confirm(f" Downloading: {ctx['interface']['arguments']}\n Do you want to continue?"):
#         # Download heatmaps
#         from pkg.chart_srv import client

#         client.begin_chart_download(ctx)
#     else:  # Print default message
#         click.echo("Goodby.")
