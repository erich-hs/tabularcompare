install:
	pip install --upgrade pip &&\
	pip install -r requirements.txt

lint:
	pylint --disable=R,C,W1203,E1101 src.tabularcompare.compare src.tabularcompare.utils --fail-under=9.0

test:
	pytest

format:
	black src/tabularcompare/*.py