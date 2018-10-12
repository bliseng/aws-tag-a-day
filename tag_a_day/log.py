import logging


def logger():
    tag_logger = logging.getLogger('tag-a-day')
    tag_logger.setLevel(level=logging.INFO)
    return tag_logger
