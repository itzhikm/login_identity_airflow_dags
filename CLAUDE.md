# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository status

`airflow_dag_spec.md` is the design source of truth; reconcile behavior changes against it as well as the code.

Layout:

```
dags/
└── identity_links_daily.py
tests/
├── airflow_logging.py        # stdlib logging config to bypass Windows-specific Airflow init issues
├── conftest.py               # bootstraps AIRFLOW_HOME and pre-imports airflow.utils.log.* before init
└── test_dag_structure.py     # DagBag-based DAG-shape tests
requirements.txt              # runtime deps
requirements-dev.txt          # adds pytest + pinned Airflow for tests
pytest.ini                    # pythonpath=dags
```

## Architecture

The DAG (`identity_links_daily`, schedule `0 2 * * *`) is a thin Airflow wrapper around a separate Docker image — `login_identity_pipeline_job` — which does the actual work.

Single task:

- `run_identity_pipeline` (DockerOperator) — runs `login_identity_pipeline_job --date {{ ds }}`. Uses `network_mode='bridge'` with `extra_hosts={'host.docker.internal': 'host-gateway'}` so the container can reach Postgres/Kafka running on the host.

### External dependencies (host services, not Airflow-managed)

- Postgres at `host.docker.internal:5432`, db `identity_db` (consumed by the pipeline container).
- Kafka at `host.docker.internal:9092` (consumed by the pipeline container).
- The `login_identity_pipeline_job` Docker image must be built and available locally before the DAG can succeed.

### DAG configuration constraints

- `catchup=False` and `max_active_runs=1` — the DAG is intentionally non-backfilling and serial.
- `retries=3`, `retry_delay=5min`, `email_on_failure=True`.
- `start_date=datetime(2026, 4, 1)`.

## Implementation conventions

- Use the Airflow macro `{{ ds }}` (YYYY-MM-DD) for the execution date passed to the container.
- The credentials in `PIPELINE_ENV` (the dict forwarded to the DockerOperator) are for the pipeline container's own clients.

## Dependencies

```
apache-airflow
apache-airflow-providers-docker      # DockerOperator
```
