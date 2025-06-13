import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logger(app=None):
    log_dir = 'logs'
    os.makedirs(log_dir, exist_ok=True)

    log_path = os.path.join(log_dir, 'app.log')
    file_handler = RotatingFileHandler(
        log_path,
        maxBytes=10240,
        backupCount=5,
        delay=True,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.INFO)

    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    )
    file_handler.setFormatter(formatter)

    if app:
        if not app.logger.handlers:
            app.logger.addHandler(file_handler)
    else:
        logger = logging.getLogger('app_logger')
        logger.setLevel(logging.INFO)
        if not logger.handlers:
            logger.addHandler(file_handler)
        return logger
