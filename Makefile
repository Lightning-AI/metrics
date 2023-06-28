.PHONY: test clean docs env data

# assume you have installed need packages
export SPHINX_MOCK_REQUIREMENTS=1

clean:
	# clean all temp runs
	rm -rf $(shell find . -name "mlruns")
	rm -rf _ckpt_*
	rm -rf .mypy_cache
	rm -rf .pytest_cache
	rm -rf tests/.pytest_cache
	rm -rf ./docs/build
	rm -rf ./docs/source/generated
	rm -rf ./docs/source/*/generated
	rm -rf ./docs/source/api
	rm -rf build
	rm -rf dist
	rm -rf *.egg-info
	rm -rf src/*.egg-info

test: clean env data
	# run tests with coverage
	cd src && python -m pytest torchmetrics
	cd tests && python -m pytest unittests -v --cov=torchmetrics
	cd tests && python -m coverage report

docs: clean
	FREEZE_REQUIREMENTS=1 pip install -e . --quiet -r requirements/docs.txt
	# apt-get install -y texlive-latex-extra dvipng texlive-pictures texlive-fonts-recommended cm-super
	python -m sphinx -b html -W --keep-going docs/source docs/build

env:
	export FREEZE_REQUIREMENTS=1
	pip install -e . -U
	pip install -r requirements/devel.txt

data:
	python -c "from urllib.request import urlretrieve ; urlretrieve('https://pl-public-data.s3.amazonaws.com/metrics/data.zip', 'data.zip')"
	unzip -o data.zip -d ./tests
