.PHONY: test docs

bootstrap:
	virtualenv .venv
	chmod +x .venv/bin/activate
	make env

env:
	( \
		source .venv/bin/activate; \
		pip install -Ur requirements_dev.txt; \
	)

env-test:
	( \
		source .venv/bin/activate; \
		flake8 pytodoist; \
		python -m pytodoist.test.test_api; \
		python -m pytodoist.test.test_todoist; \
	)

test:
	flake8 pytodoist
	python -m pytodoist.test.test_api
	python -m pytodoist.test.test_todoist

docs:
	cd ./docs && $(MAKE) clean && $(MAKE) html

testupload:
	python setup.py sdist upload -r testpypi
	python setup.py sdist bdist_wheel upload -r testpypi

upload:
	python setup.py sdist upload -r pypi
	python setup.py sdist bdist_wheel upload -r pypi
