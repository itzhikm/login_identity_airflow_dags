"""Minimal stdlib-only logging config for Airflow tests on Windows.

Airflow's default logging config references formatter classes inside
``airflow.utils.log.*``. On Windows those references trigger a circular
import during ``airflow.__init__``. This config sidesteps that by using
only ``logging.Formatter`` and ``logging.StreamHandler``.
"""
from __future__ import annotations

LOGGING_CONFIG: dict = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "mask_secrets": {
            "()": "airflow.utils.log.secrets_masker.SecretsMasker",
        },
    },
    "formatters": {
        "airflow": {
            "format": "[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "airflow",
            "stream": "ext://sys.stdout",
            "filters": ["mask_secrets"],
        },
        # Name must match the value of [logging] task_log_reader (default 'task').
        "task": {
            "class": "logging.StreamHandler",
            "formatter": "airflow",
            "stream": "ext://sys.stdout",
            "filters": ["mask_secrets"],
        },
        "processor": {
            "class": "logging.StreamHandler",
            "formatter": "airflow",
            "stream": "ext://sys.stdout",
            "filters": ["mask_secrets"],
        },
    },
    "loggers": {
        "airflow": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "airflow.task": {"handlers": ["task"], "level": "INFO", "propagate": False},
        "airflow.processor": {"handlers": ["processor"], "level": "INFO", "propagate": False},
    },
    "root": {"handlers": ["console"], "level": "INFO"},
}
