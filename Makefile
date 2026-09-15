.PHONY: all test verify serve clean

all: test verify

test:
	python3 tests/run_all_tests.py

verify:
	python3 scripts/verify_fair_compliance.py

serve:
	python3 scripts/run_explorer.py --serve --port 8088

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
