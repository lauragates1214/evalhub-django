.PHONY: test-unit test-all test-ft

test-unit:
	python src/manage.py test accounts surveys

test-ft:
	python src/manage.py test functional_tests

test-all:
	python src/manage.py test accounts surveys functional_tests