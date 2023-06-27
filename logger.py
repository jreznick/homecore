import logging


def make_logger(name: str):
    services_logger = setup_logger(__name__, F'/home/compadre/logs/{name}.log')

    return services_logger


def setup_logger(name: str, log_file: str, level=logging.INFO):
    """
    configure a services logger
    :param name: the repr of the application being logged
    :param log_file: the absolute path to the log
    """

    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger


client = 'myClient'
mylogger = make_logger(client)
