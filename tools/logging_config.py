"""
@File  : log_config.py
@Author: lee
@Date  : 2022/7/13/0013 11:08:55
@Desc  :
"""
import logging
import sys

LOGGING_CONFIG = dict(
    version=1,
    disable_existing_loggers=False,
    loggers={
        # 新曾自定义日志，用于数据采集程序
        "publish_log": {
            "level": "INFO",
            "handlers": ["console", "publish_log"],
            "propagate": True,
            "qualname": "publish_log.debug",
        },
        "subscribe_log": {
            "level": "DEBUG",
            "handlers": ["console", "subscribe_log"],
            "propagate": True,
            "qualname": "subscribe_log.debug",
        }
    },
    handlers={
        # 数据采集程序控制台输出handler
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "generic",
            "stream": sys.stdout,
        },
        "publish_log": {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'log/publish_log/publish_log.log',
            'maxBytes': 10 * 1024 * 1024,
            'delay': True,
            "formatter": "generic",
            "backupCount": 20,
            "encoding": "utf-8"
        },
        "subscribe_log": {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'log/subscribe_log/subscribe_log.log',
            'maxBytes': 10 * 1024 * 1024,
            'delay': True,
            "formatter": "generic",
            "backupCount": 20,
            "encoding": "utf-8"
        }
    },
    formatters={
        # 自定义文件格式化器
        "generic": {
            "format": "%(asctime)s [%(filename)s:%(lineno)d] [%(levelname)s] %(message)s",
            "datefmt": "[%Y-%m-%d %H:%M:%S]",
            "class": "logging.Formatter",
        }
    },
)
publish_log = logging.getLogger("publish_log")
subscribe_log = logging.getLogger("subscribe_log")
