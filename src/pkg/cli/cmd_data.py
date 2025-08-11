"""src/pkg/cli/cmd_data.py"""

import logging

import click

from pkg import DEBUG


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
""",
)
@click.argument("arguments", nargs=-1, default=None, required=False, type=str)

# @click.pass_context
@click.pass_obj
def cli(ctx, arguments):
    """Run data command"""
    if DEBUG:
        logger.debug(f"start_cli(ctx={type(ctx)}, arguments={arguments})")

    ctx["interface"]["command"] = "data"

    # add arguments to interface ctx and set database name
    if arguments:  # use symbols in arguments list
        ticker_list = sorted([i.upper() for i in list(arguments)])
        ctx["interface"]["database"] = click.prompt(
            f"* Using database 'custom.db'. Type a new database name to change,\n  press Enter to accept.",
            default="custom.db",
        )
    else:  # use symbols from default ticker list
        if ctx["data_service"]["data_list"]:
            ticker_list = sorted(list(ctx["data_service"]["data_list"].split(" ")))
        else:
            try:
                ticker_list = sorted(list(ctx["default"]["ticker"].split(" ")))
            except:
                click.echo(message="Add tickers to data_list in data_service/cfg_data.ini file.")

        ctx["interface"]["database"] = click.prompt(
            f"* Using database 'default.db'. Type a new database name to change,\n  press Enter to accept",
            default="default.db",
        )
    ctx["interface"]["ticker"] = ticker_list

    data_line = click.prompt(
        f"* Using data line '{ctx['data_service']['data_line']}'. Type a new value to change,\n  press Enter to accept",
        default=ctx["data_service"]["data_line"],
    )
    ctx["interface"]["data_line"] = sorted([i.upper() for i in data_line.split(" ")])

    ctx["interface"]["window_size"] = click.prompt(
        f"* Using sliding window size {ctx['default']['window_size']}. Type a new value to change,\n  press Enter to accept",
        default=ctx["default"]["window_size"],
    )

    if click.confirm(
        f"* Saving {ctx['interface']['data_line']} for {ctx['interface']['ticker']} to '{ctx['interface']['database']}.\n  Do you want to continue?"
    ):
        from pkg.data_srv import client

        client.fetch_stonk_data(ctx=ctx)

        if not DEBUG:
            print(
                f" Saved data to '{ctx['default']['work_dir']}{ctx['interface']['command']}/{ctx['interface']['database']}'\n"
            )
