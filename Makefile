UNAME := $(shell uname)



.PHONY: setup
## setup: setup project enviroments
setup:
ifeq ($(UNAME),Linux)
	bash ./bin/setup.sh
else ifeq ($(UNAME), Solaris)
	echo others $(UNAME) $(UNAME)
else ifeq ($(UNAME), Darwin)
	echo 'mac os'
endif

.PHONY: init
## init: install requirements
init:
	pip install pipenv
	pipenv install --dev

.PHONY: check
## check: check if everything's okay
check:
	isort --check-only src tests
	black -S -l 79 --check src tests
	pylint src
	mypy src

.PHONY: format
## format: format files
format:
	isort --atomic src tests
	black -S -l 79 src tests

.PHONY: test
## test: run tests
test:
	python -m pytest

.PHONY: coverage
## coverage: run tests with coverage
coverage:
	python -m pytest --cov src --cov-report term --cov-report xml

.PHONY: htmlcov
## htmlcov: run tests with coverage and create coverage report HTML files
htmlcov:
	python -m pytest --cov src --cov-report html
	rm -rf /tmp/htmlcov && mv htmlcov /tmp/
	open /tmp/htmlcov/index.html

.PHONY: requirements
## requirements: update requirements.txt
requirements:
	pipenv requirements >> requirements.txt
	pipenv requirements --dev >> requirements-dev.txt


.PHONY: build
## build: build executable package
build:
	pyinstaller --clean --noconfirm --log-level=WARN --distpath=dist --workpath=build src.spec

.PHONY: run
## run: Quick command execution for easy development
run:
	python src example/simple/wf.js


.PHONY: help
## help: prints this help message
help:
	@echo "Usage: \n"
	@sed -n 's/^##//p' ${MAKEFILE_LIST} | column -t -s ':'
