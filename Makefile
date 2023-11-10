init: 
	pip install -r requirements.txt

test:
	pytest -ra

coverage:
	coverage erase
	coverage run --include=jgrab_processing/* -m pytest -ra
	coverage report -m

lint:
	flake8 jgrab_processing
	
push:
	git push && git push --tags

.PHONY: init test