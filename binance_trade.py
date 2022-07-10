from clients import BinanceClient
from logging.handlers import RotatingFileHandler
from time import gmtime
from processors import process_all
import asyncio
import argparse
import logging
import yaml
import sys


def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-sf', '--settings_file',
                        action='store',
                        type=str,
                        required=True)
    return parser.parse_args()


def main():
    args = get_arguments()

    logging.Formatter.converter = gmtime
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(threadName)s - %(module)s: -"
                                   " %(levelname)s - %(message)s",
        handlers=[RotatingFileHandler(f"./logs/application.log",
                                      maxBytes=10485760, backupCount=5)
                  ])

    logging.info(f"loading settings from {args.settings_file}")
    with open(args.settings_file, "r") as settings_file:
        try:
            settings = yaml.safe_load(settings_file)
        except yaml.YAMLError as err:
            logging.fatal(f"unable to load settings yaml: {err}")
            sys.exit(1)

    client_init_data = settings.get("binance_client")
    market_init_data = settings.get("market")

    logging.info("initialising Binance client")
    binance_client = BinanceClient(
        client_init_data.get("key"),
        client_init_data.get("secret"),
        client_init_data.get("test_net"),
        client_init_data.get("test_buy")
    )

    while True:
        loop = asyncio.get_event_loop()
        task = [loop.create_task(process_all(
            binance_client, data))
            for data in market_init_data]
        loop.run_until_complete(
            asyncio.wait(task))


if __name__ == "__main__":
    main()
