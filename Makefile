.PHONY: test docs

test:
	flake8 pytodoist
	python -m pytodoist.test.test_api
	python -m pytodoist.test.test_todoist

docs:
	cd ./docs && $(MAKE) clean && $(MAKE) html
