import logging
from logging.handlers import RotatingFileHandler


def get_logger(
        FORMAT     = '%(levelname)s %(asctime)s %(message)s',
        NAME       = '',
        FILE_INFO  = 'info.log',
        FILE_ERROR = 'errors.log',
        MODE = 'a+',
        MAXBYTES = 5*1024*1024,
        BACKUP_COUNT = 5
                ):

    logger = logging.getLogger(NAME)
    log_formatter = logging.Formatter(FORMAT)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(log_formatter)
    logger.addHandler(stream_handler)

    file_handler_info = RotatingFileHandler(FILE_INFO, MODE, MAXBYTES, BACKUP_COUNT)
    file_handler_info.setFormatter(log_formatter)
    file_handler_info.setLevel(logging.DEBUG)
    logger.addHandler(file_handler_info)

    file_handler_error = RotatingFileHandler(FILE_ERROR, MODE, MAXBYTES, BACKUP_COUNT)
    file_handler_error.setFormatter(log_formatter)
    file_handler_error.setLevel(logging.WARNING)
    logger.addHandler(file_handler_error)

    logger.setLevel(logging.INFO)

    return logger