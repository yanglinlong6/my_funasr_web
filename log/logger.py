import logging
import os
import sys
from logging.handlers import TimedRotatingFileHandler

def setup_logging(log_file):
    """
    设置日志记录器，将日志输出到文件并按天进行保存
    :param log_file: 日志文件路径
    """
    # 创建一个日志记录器
    logger = logging.getLogger(log_file)
    if logger.hasHandlers():
        logger.handlers.clear()

    logger.setLevel(logging.DEBUG)

    # 创建一个 TimedRotatingFileHandler 实例，将日志输出到文件，并按天进行保存
    file_handler = TimedRotatingFileHandler(filename=log_file, when="midnight", interval=1, backupCount=30,encoding='UTF-8')
    file_handler.setLevel(logging.DEBUG)

    # 设置日志格式
    formatter = logging.Formatter('%(asctime)s %(thread)d %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    # 将处理器添加到日志记录器中
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

# log=setup_logging('%s/funasr_temp.log' % "/app/soft/python_project/audio_dev/logs")
log = setup_logging("./funasr_temp.log")
