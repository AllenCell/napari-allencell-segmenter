.PHONY: clean build test


clean:  ## clean all build, python, and testing files
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +
	rm -fr .tox/
	rm -fr .coverage
	rm -fr coverage.xml
	rm -fr htmlcov/
	rm -fr .pytest_cache

build: ## run tox / run tests and lint
	tox

test: ## run pytest with coverage report
	pytest --cov=napari_allencell_segmenter --cov-report xml --cov-report term

lint: ## run a lint check / report
	flake8 napari_allencell_segmenter --count --verbose --show-source --statistics
	black --check --exclude vendor napari_allencell_segmenter

lint-format: ## reformat files with black
	black --exclude vendor napari_allencell_segmenter -l 120