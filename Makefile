.PHONY: test docs

test:
	python -m pytodoist.test.api
	python -m pytodoist.test.todoist

docs:
	cd ./docs && $(MAKE) clean && $(MAKE) html

pep8:
	pep8 pytodoist/*.py
	pep8 pytodoist/test/*.py