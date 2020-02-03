#!/usr/bin/env bash

airflow connections --delete --conn_id postgres
airflow connections --add --conn_id postgres --conn_type postgres --conn_host ${POSTGRES_HOST} --conn_port ${POSTGRES_PORT} --conn_login ${POSTGRES_LOGIN} --conn_password ${POSTGRES_PASSWORD} --conn_schema ${POSTGRES_DB}

airflow connections --delete --conn_id airflow_db
airflow connections --add --conn_id airflow_db --conn_type postgres --conn_host ${POSTGRES_AIRFLOW_HOST} --conn_port ${POSTGRES_AIRFLOW_PORT} --conn_login ${POSTGRES_AIRFLOW_LOGIN} --conn_password ${POSTGRES_AIRFLOW_PASSWORD} --conn_schema ${POSTGRES_AIRFLOW_DB}

airflow connections --delete --conn_id github
airflow connections --add --conn_id github --conn_type http --conn_login ${GITHUB_LOGIN} --conn_password ${GITHUB_PASSWORD}
