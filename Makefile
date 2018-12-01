.PHONY: test docs

test:
	flake8 pytodoist
	python -m pytodoist.test.test_api
	python -m pytodoist.test.test_todoist

docs:
	cd ./docs && $(MAKE) clean && $(MAKE) html

testupload:
	python setup.py sdist
	python setup.py sdist bdist_wheel
	twine upload dist/* -r testpypi

upload:
	python setup.py sdist
	python setup.py sdist bdist_wheel
	twine upload dist/* -r pypi
