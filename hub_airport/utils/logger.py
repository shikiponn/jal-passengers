import logging
from typing import List, Optional


class IgnoreFilter(logging.Filter):

    def __init__(self, ignore: List):
        """
        log msgを単語でfilerする、未使用
        Args:
            ignore: List of str you want to ignore in log

        """
        super().__init__()
        self.ignore = ignore

    def filter(self, record):
        log_msg = record.getMessage()
        # logにignoreに含まれる単語があればFalseを返して記録しない
        is_valid_msg = not any(elm in log_msg for elm in self.ignore)
        return is_valid_msg


def init_root_logger(dir_log: Optional[str] = None,
                fmt: Optional[str] = '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                date_fmt: Optional[str] = "%Y-%m-%d %H:%M:%S") -> logging.Logger:
    """
    Create logger to call from user script

    Args:
        dir_log: path to your log file
        fmt:
        date_fmt:
    Returns:
        logging.Logger

    Examples:
        from zoo.util.logger import init_root_logger
        logger = init_root_logger()
        # If you want to use file handler
        # logger = init_root_logger(dir_log='./log.txt')

        logger.info('logging info')
        logger.debug('logging debug')
    """

    # TODO: FileHandler, RotatingFileHandlerを追加
    # https://qiita.com/shotakaha/items/0fa2db1dc8253c83e2bb
    # https://docs.python.org/3/howto/logging-cookbook.html
    # https://qiita.com/knknkn1162/items/87b1153c212b27bd52b4#fn4
    # https://qiita.com/__init__/items/91e5841ed53d55a7895e
    # TODO: levelを可変にする
    logging.basicConfig(level=logging.DEBUG,
                        # filename=dir_log,
                        format=fmt,
                        datefmt=date_fmt)

    if dir_log:
        # File handlerを追加してログファイルに書き出す
        fh = logging.FileHandler(dir_log)
        fh_formatter = logging.Formatter(fmt, datefmt=date_fmt)
        fh.setFormatter(fh_formatter)
        # TODO: 可変にする
        fh.setLevel(logging.DEBUG)
        logging.getLogger().addHandler(fh)

    return logging
