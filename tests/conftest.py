from __future__ import annotations

import os
from pathlib import Path

# Pin AIRFLOW_HOME to a project-local dir BEFORE airflow is imported. The
# default (~/airflow) resolves to a path Windows can't create.
_AIRFLOW_HOME = Path(__file__).resolve().parent.parent / ".airflow_home"
_AIRFLOW_HOME.mkdir(exist_ok=True)
os.environ.setdefault("AIRFLOW_HOME", str(_AIRFLOW_HOME))

# Postgres env vars consumed by identity_links_daily._get_pg_conn at call time.
os.environ.setdefault("POSTGRES_HOST", "localhost")
os.environ.setdefault("POSTGRES_PORT", "5432")
os.environ.setdefault("POSTGRES_DB", "identity_db")
os.environ.setdefault("POSTGRES_USER", "postgres")
os.environ.setdefault("POSTGRES_PASSWORD", "postgres")

os.environ.setdefault("AIRFLOW__CORE__UNIT_TEST_MODE", "True")
os.environ.setdefault("AIRFLOW__CORE__LOAD_EXAMPLES", "False")

# Break the airflow-init circular import on Windows.
#
# Airflow's __init__.py calls settings.initialize() which calls dictConfig()
# with a logging config that references airflow.utils.log.* classes by dotted
# path. dictConfig resolves these via getattr(airflow, 'utils'), which fails
# because airflow.__init__ is still mid-execution and hasn't imported the
# `utils` subpackage yet.
#
# The escape hatch at airflow/__init__.py:73 — `_AIRFLOW__AS_LIBRARY` — skips
# settings.initialize() entirely. We use it to import airflow first, then
# pre-import the utils submodules so they're attached to the airflow package,
# then clear the flag and run initialize() manually.
def _bootstrap_airflow_for_windows() -> None:
    import importlib

    os.environ["_AIRFLOW__AS_LIBRARY"] = "1"
    try:
        importlib.import_module("airflow")
        for submod in (
            "airflow.utils",
            "airflow.utils.log",
            "airflow.utils.log.secrets_masker",
            "airflow.utils.log.timezone_aware",
            "airflow.utils.log.colored_log",
            "airflow.utils.log.logging_mixin",
            "airflow.utils.log.file_task_handler",
            "airflow.utils.log.file_processor_handler",
        ):
            importlib.import_module(submod)
    finally:
        del os.environ["_AIRFLOW__AS_LIBRARY"]

    from airflow import settings
    settings.initialize()


_bootstrap_airflow_for_windows()
