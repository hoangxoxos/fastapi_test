import logging
import logging.config


def configure_logging(level: str) -> None:
    log_level = getattr(logging, level.upper(), None)
    if not isinstance(log_level, int):
        raise TypeError(f"Invalid log level: {level}")

    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "%(asctime)s %(levelname)s [%(name)s] %(message)s",
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                }
            },
            "root": {
                "level": log_level,
                "handlers": ["console"],
            },
        }
    )
