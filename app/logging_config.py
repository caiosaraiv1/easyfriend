"""
app/logging_config.py
Configuração centralizada de logging do EasyFriend.
Grava logs no terminal (INFO+) e em arquivo (DEBUG+).
"""

import logging
import logging.handlers
import os
from datetime import datetime

# Pasta de logs
LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, f"easyfriend_{datetime.now().strftime('%Y%m%d')}.log")

def setup_logging():
    """Configura e retorna o logger raiz da aplicação."""

    # Formato com timestamp, nível e módulo
    fmt = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    date_fmt = "%Y-%m-%d %H:%M:%S"
    formatter = logging.Formatter(fmt, datefmt=date_fmt)

    # Handler de terminal — INFO e acima
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # Handler de arquivo — DEBUG e acima, rotaciona diariamente
    file_handler = logging.handlers.TimedRotatingFileHandler(
        LOG_FILE, when="midnight", backupCount=7, encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    # Logger raiz
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

    return root_logger


def get_logger(name: str) -> logging.Logger:
    """Retorna um logger nomeado para usar em qualquer módulo."""
    return logging.getLogger(name)
