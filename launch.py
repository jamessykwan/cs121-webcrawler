from configparser import ConfigParser
from argparse import ArgumentParser

from utils.server_registration import get_cache_server
from utils.config import Config
from crawler import Crawler
import globals

def main(config_file, restart):
    cparser = ConfigParser()
    cparser.read(config_file)
    config = Config(cparser)
    config.cache_server = get_cache_server(config, restart)
    crawler = Crawler(config, restart)
    crawler.start()
    print(f"Most content url: {globals.longest_page_url} with number of token(stop word) {globals.longest_page_val}")
    print(f"Number of unique pages {globals.unique_pages}")
    #sorting big token_freq, get top 50
    sorted_freqs = sorted(globals.token_freq.items(), key=lambda x:x[1],reverse=True)
    print(f"Freq dic {sorted_freqs[:50]}")


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--restart", action="store_true", default=False)
    parser.add_argument("--config_file", type=str, default="config.ini")
    args = parser.parse_args()
    main(args.config_file, args.restart)
