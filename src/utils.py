import importlib
import json
import sys
from argparse import ArgumentParser
from datetime import datetime
from pathlib import Path


def load_config():
    config_path = Path(__file__).parent / "user.json"

    if "-c" in sys.argv or "--config" in sys.argv:
        idx = sys.argv.index("-c" if "-c" in sys.argv else "--config") + 1

        config_path = Path(sys.argv[idx]).expanduser().resolve()

    if config_path.exists():
        return json.loads(config_path.read_bytes())


def get_loader_class(config):
    # Load data loader from config. Default loader is EODFileLoader
    loader_name = config.get("LOADER", "EODFileLoader")

    loader_module = importlib.import_module(f"loaders.{loader_name}")

    return getattr(loader_module, loader_name)


def parse_cli_options():
    # Add CLI options
    parser = ArgumentParser(
        description="Python CLI tool to plot RRG charts",
        epilog="https://github.com/BennyThadikaran/RRG-Lite",
    )

    parser.add_argument(
        "-c",
        "--config",
        type=lambda x: Path(x).expanduser().resolve(),
        metavar="filepath",
        help="Custom config file",
    )

    parser.add_argument(
        "-d",
        "--date",
        type=datetime.fromisoformat,
        metavar="str",
        help="ISO format date YYYY-MM-DD.",
    )

    parser.add_argument(
        "--tf",
        action="store",
        default="weekly",
        help="Timeframe string.",
    )

    parser.add_argument(
        "-t",
        "--tail",
        type=int,
        default=3,
        metavar="int",
        help="Length of tail. Default 3",
    )

    parser.add_argument(
        "-b",
        "--benchmark",
        default=None,
        metavar="str",
        help="Benchmark index name",
    )

    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument(
        "-f",
        "--file",
        type=lambda x: Path(x).expanduser().resolve(),
        default=None,
        metavar="filepath",
        help="File containing list of stocks. One on each line",
    )

    group.add_argument(
        "--sym",
        nargs="+",
        metavar="SYM",
        help="Space separated list of stock symbols.",
    )

    group.add_argument(
        "-v",
        "--version",
        action="store_true",
        help="Print the current version.",
    )

    return parser.parse_args()
