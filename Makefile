.PHONY: test docs pep8

test:
	python -m pytodoist.test.test_api
	python -m pytodoist.test.test_todoist

docs:
	cd ./docs && $(MAKE) clean && $(MAKE) html

pep8:
	pep8 pytodoist/*.py
	pep8 pytodoist/test/*.py