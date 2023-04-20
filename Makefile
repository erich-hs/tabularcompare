install:
	pip install --upgrade pip &&\
	pip install -r requirements.txt
	pip install .

lint:
	pylint --disable=R,C,W1203,E1101 src.tabularcompare.compare src.tabularcompare.utils --fail-under=9.0

test:
	python -m pytest tests/test_compare.py &&\
		python -m pytest tests/test_app.py

format:
	black src/tabularcompare/*.py