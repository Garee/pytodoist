.PHONY: test docs

test:
	python -m pytodoist.test.api
	python -m pytodoist.test.todoist

docs:
	cd ./docs && $(MAKE) clean && $(MAKE) html