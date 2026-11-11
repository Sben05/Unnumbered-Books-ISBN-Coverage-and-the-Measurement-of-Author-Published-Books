PYTHON ?= $(if $(wildcard .venv/bin/python),.venv/bin/python,python3)

.PHONY: reproduce analysis paper check test

reproduce: analysis paper check

analysis:
	$(PYTHON) analysis/analyze.py
	$(PYTHON) analysis/make_tables.py

paper:
	$(PYTHON) analysis/build_paper.py

check:
	$(PYTHON) analysis/check_paper.py

test:
	$(PYTHON) -m unittest discover -s tests
