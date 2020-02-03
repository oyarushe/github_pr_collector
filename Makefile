.PHONY: run
run:
	docker-compose up -d --build airflow postgres

.PHONY: clean
clean:
	docker-compose down

.PHONY: airflow-bash
airflow-bash:
	docker-compose exec airflow bash

.PHONY: airflow-logs
airflow-logs:
	docker-compose logs -f airflow

.PHONY: init-db
init-db:
	docker-compose exec airflow datarobot init-db

.PHONY: lint
lint:
	docker-compose exec airflow flake8 --config .flake8 dags plugins airflow-utils/

.PHONY: test
test:
	docker-compose exec airflow python -m pytest tests
