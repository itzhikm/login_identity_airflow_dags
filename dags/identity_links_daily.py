from __future__ import annotations

from datetime import datetime, timedelta

from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator

DAG_ID = "identity_links_daily"
PIPELINE_IMAGE = "login_identity_pipeline_job"

# Env vars passed to the pipeline container — only for the container's own
# DB/Kafka clients.
PIPELINE_ENV = {
    "KAFKA_BOOTSTRAP_SERVERS": "kafka:9092",
    "POSTGRES_HOST": "host.docker.internal",
    "POSTGRES_PORT": "5432",
    "POSTGRES_DB": "identity_db",
    "POSTGRES_USER": "postgres",
    "POSTGRES_PASSWORD": "postgres",
}


default_args = {
    "owner": "data-engineering",
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
    "email_on_failure": True,
}

with DAG(
    dag_id=DAG_ID,
    schedule="0 2 * * *",
    start_date=datetime(2026, 4, 1),
    catchup=False,
    max_active_runs=1,
    default_args=default_args,
    tags=["identity", "daily"],
) as dag:
    run_pipeline = DockerOperator(
        task_id="run_identity_pipeline",
        image=PIPELINE_IMAGE,
        command="--date {{ ds }}",
        auto_remove="success",
        docker_url="unix:///var/run/docker.sock",
        network_mode="kafka-compose_default",
        mount_tmp_dir=False,
        extra_hosts={
            "host.docker.internal": "host-gateway",
            "kafka": "host-gateway",
        },
        environment=PIPELINE_ENV,
    )
