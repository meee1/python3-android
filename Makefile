PYTHON?=python

all:
	$(PYTHON) -m pybuild

clean:
	$(PYTHON) -m pybuild.clean

test:
	$(PYTHON) -m pybuild.check_cpython_modules

send:
	$(PYTHON) -m pybuild.send

download_sources:
	$(PYTHON) -m pybuild.download_sources

.PHONY: all clean test send
