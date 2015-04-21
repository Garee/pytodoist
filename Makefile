.PHONY: test docs

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
