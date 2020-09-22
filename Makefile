.PHONY: build

POSTGRES_USER ?= postgres
PSQL ?= docker-compose exec postgres psql
PIP_INDEX = https://mirrors.aliyun.com/pypi/simple/

export READ_DOT_ENV_FILE=True

install:
	pip install --upgrade --index-url ${PIP_INDEX} pip
	pip install --upgrade --index-url ${PIP_INDEX} -r requirements/local.txt

pyenv-%:
	pyenv virtualenv $* eam
	pyenv local eam
	make install

up:
	docker-compose up -d --remove-orphans
	docker-compose ps

test:
	make gqlgt-schema
	pytest -s -v --cov=app --cov-report term-missing -c pytest.ini --alluredir=./dist/allure tests

# prepare install allure by `brew install allure` in macos
test-report: test
	allure serve ./dist/allure

build:
	docker build -t dcr.teletraan.io/public/interagent:latest .

push: build
	docker push dcr.teletraan.io/public/interagent:latest

migrations-%:
	alembic revision --autogenerate -m "$*"

downdb-%:
	alembic downgrade $*

migrate:
	alembic upgrade head

cleardb:
	alembic downgrade base

gen:
	gqlgen -f ./schema.graphql all > app/schema_types.py

recreate-db-%:
	${PSQL} -U ${POSTGRES_USER} -c "drop database \"$*\""
	${PSQL} -U ${POSTGRES_USER} -c "create database \"$*\" owner ${POSTGRES_USER}"
	${PSQL} -U ${POSTGRES_USER} -c  "grant all privileges on database \"$*\" to ${POSTGRES_USER}"

run:
	python main.py
