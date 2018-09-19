import os
import sys

from pydmcharting_logging import logging
logger = logging.getLogger(__name__)


def setup_paths():
    try:
        pydm_path = os.environ["PYDM_PATH"]
    except KeyError as error:
        logger.error("You must set up the appropriate environment variables. Missing env var: {0}".format(error))
        return
    sys.path.insert(1, pydm_path)
