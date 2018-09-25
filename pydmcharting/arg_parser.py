import argparse
import sys

from pydmcharting_logging import logging
logger = logging.getLogger(__name__)


class ArgParser(argparse.ArgumentParser):
    def error(self, message):
        logger.error("Argument parsing error: {0}".format(message))
        self.print_help()
        sys.exit(2)

