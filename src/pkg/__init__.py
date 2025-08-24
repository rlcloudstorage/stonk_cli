"""src/pkg/__init__.py"""

import logging, logging.config
import os

from configparser import ConfigParser

from dotenv import load_dotenv

load_dotenv()

root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
src_dir = os.path.join(root_dir, "src/")

# check 'work_dir' exists, if not create it
os.makedirs(os.path.join(root_dir, "work_dir"), exist_ok=True)
work_dir = os.path.join(root_dir, "work_dir/")
pkg_dir = os.path.join(root_dir, "src/pkg")
config_file = os.path.join(src_dir, "config.ini")
logger_conf = os.path.join(src_dir, "logger.ini")

logging.config.fileConfig(fname=logger_conf)
logger = logging.getLogger(f"  === Starting stonk_cli app - src/{__name__}/__init__.py ===")

# Create getlist() converter, used for reading ticker symbols
config_obj = ConfigParser(allow_no_value=True, converters={"list": lambda x: [i.strip() for i in x.split(",")]})

# Create default config file if if does not exist
if not os.path.isfile(config_file):

    # Add the structure to the configparser object
    config_obj.add_section("default")
    config_obj.add_section("interface")
    config_obj.set('default', 'debug', 'True')

    # Write the structure to the new file
    with open(config_file, "w") as cf:
        cf.truncate()
        config_obj.write(cf)

# Config file exists, create configparser object
try:
    config_obj.read(config_file)
except Exception as e:
    logger.debug(f"{e} - {config_file}")

config_obj.read(config_file)

# Gather config files from other apps
for root, dirs, files in os.walk(pkg_dir):
    for filename in files:
        if filename.startswith("cfg_") and filename.endswith(".ini"):

            # put name and path in 'default' section, to be read into confg_dict later
            config_obj.set("default", filename.removesuffix(".ini"), os.path.join(root, filename))

            # read '.ini' paths into configparser object
            config_obj.read(os.path.join(root, filename))

# Put config section/option data into a dictionary
config_dict = dict(
    (section, dict((option, config_obj.get(section, option)) for option in config_obj.options(section)))
    for section in config_obj.sections()
)

# Convert 'debug' string into a boolean value
config_dict["default"]["debug"] = config_obj.getboolean("default", "debug")
DEBUG = config_dict["default"]["debug"]

# Add to config_dict
if os.getenv("CHART_LIST"):
    config_dict["default"]["chart_list"] = os.getenv("CHART_LIST")
if os.getenv("OHLC_TIC_LIST"):
    config_dict["default"]["ohlc_tic_list"] = os.getenv("OHLC_TIC_LIST")
if os.getenv("SIGNAL_TIC_LIST"):
    config_dict["default"]["signal_tic_list"] = os.getenv("SIGNAL_TIC_LIST")
config_dict["default"]["work_dir"] = work_dir
config_dict["default"]["cfg_main"] = config_file

# Print/log some debug information
if DEBUG:
    logger.debug(f"""
    root_dir: {root_dir}
    src_dir: {src_dir}
    work_dir: {work_dir}
    pkg_dir: {pkg_dir}
    logger_conf: {logger_conf}
    config_file: {config_file}
    config_dict: {config_dict}
""")

# Choose user interface
def run_cli():
    """see 'pyproject.toml' - entry point for CLI"""
    from .cli import main_console

    main_console.start_cli()
