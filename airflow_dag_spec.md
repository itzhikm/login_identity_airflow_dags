# Airflow DAG Spec for Claude Code

## Overview
A daily Airflow DAG that triggers the `login_identity_pipeline_job` Docker container.
The DAG runs every day at 02:00 AM and passes the execution date to the job.

---

## DAG Details

```
DAG ID:   identity_links_daily
Schedule: 0 2 * * *  (every day at 02:00 AM)
```

---

## Project Structure
```
dags/
└── identity_links_daily.py
```

---

## Tasks

```
1. run_identity_pipeline   (DockerOperator)
```

---

## Task: run_identity_pipeline

```
Type: DockerOperator

Image: login_identity_pipeline_job

Command:
  --date {{ ds }}   # Airflow execution date in YYYY-MM-DD format

Docker run equivalent:
  docker run --rm \
    --add-host=host.docker.internal:host-gateway \
    --env-file .env \
    login_identity_pipeline_job \
    --date 2026-04-28

Environment variables passed to container:
  KAFKA_BOOTSTRAP_SERVERS=host.docker.internal:9092
  POSTGRES_HOST=host.docker.internal
  POSTGRES_PORT=5432
  POSTGRES_DB=identity_db
  POSTGRES_USER=postgres
  POSTGRES_PASSWORD=postgres

DockerOperator settings:
  auto_remove=True          # remove container after run
  network_mode='bridge'
  extra_hosts:              # equivalent to --add-host
    host.docker.internal: host-gateway
```

---

## DAG Configuration

```python
default_args = {
    'owner':            'data-engineering',
    'retries':          3,
    'retry_delay':      timedelta(minutes=5),
    'email_on_failure': True,
}

DAG(
    dag_id          = 'identity_links_daily',
    schedule        = '0 2 * * *',
    start_date      = datetime(2026, 4, 1),
    catchup         = False,       # do not backfill missed runs
    max_active_runs = 1,           # prevent parallel runs
    default_args    = default_args,
)
```

---

## Environment Variables (passed to pipeline container)

```bash
POSTGRES_HOST=host.docker.internal
POSTGRES_PORT=5432
POSTGRES_DB=identity_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
KAFKA_BOOTSTRAP_SERVERS=host.docker.internal:9092
```

---

## requirements.txt

```
apache-airflow
apache-airflow-providers-docker
```

---

## Implementation Notes
- Use `{{ ds }}` Airflow macro for execution date (format: YYYY-MM-DD)
- DockerOperator requires `apache-airflow-providers-docker` provider
- `catchup=False` ensures only the latest run executes on first deploy
- `max_active_runs=1` prevents overlapping runs
