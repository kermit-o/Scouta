import logging, logging.config
def setup_logging() -> None:
    cfg = {
        "version": 1,
        "formatters": {"default": {"format": "%(asctime)s %(levelname)s [%(name)s] %(message)s"}},
        "handlers": {"console": {"class": "logging.StreamHandler", "formatter": "default"}},
        "root": {"level": "INFO", "handlers": ["console"]},
    }
    logging.config.dictConfig(cfg)
