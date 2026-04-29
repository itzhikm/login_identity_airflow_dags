from __future__ import annotations

import pytest
from airflow.models import DagBag


@pytest.fixture(scope="module")
def dagbag() -> DagBag:
    return DagBag(dag_folder="dags", include_examples=False)


@pytest.fixture(scope="module")
def dag(dagbag: DagBag):
    return dagbag.get_dag("identity_links_daily")


def test_dag_imports_without_errors(dagbag: DagBag) -> None:
    assert dagbag.import_errors == {}, f"DAG import errors: {dagbag.import_errors}"


def test_dag_is_registered(dag) -> None:
    assert dag is not None, "identity_links_daily DAG was not found in dagbag"


def test_schedule_is_2am_daily(dag) -> None:
    # Airflow 2 surfaces this as schedule_interval; in 3 it's timetable. The
    # cron string is what we care about.
    schedule = getattr(dag, "schedule_interval", None) or getattr(dag, "schedule", None)
    assert str(schedule) == "0 2 * * *"


def test_catchup_disabled_and_serial(dag) -> None:
    assert dag.catchup is False
    assert dag.max_active_runs == 1


def test_default_args(dag) -> None:
    assert dag.default_args["owner"] == "data-engineering"
    assert dag.default_args["retries"] == 3
    assert dag.default_args["email_on_failure"] is True


def test_expected_tasks_present(dag) -> None:
    assert {t.task_id for t in dag.tasks} == {"run_identity_pipeline"}


def test_docker_task_configured(dag) -> None:
    docker_task = dag.get_task("run_identity_pipeline")
    assert docker_task.image == "login_identity_pipeline_job"
    assert "{{ ds }}" in docker_task.command
    assert docker_task.network_mode == "bridge"
    assert docker_task.extra_hosts == {"host.docker.internal": "host-gateway"}
    # Required env vars are forwarded to the container.
    for key in (
        "POSTGRES_HOST",
        "POSTGRES_PORT",
        "POSTGRES_DB",
        "POSTGRES_USER",
        "POSTGRES_PASSWORD",
        "KAFKA_BOOTSTRAP_SERVERS",
    ):
        assert key in docker_task.environment, f"missing {key} in DockerOperator env"
