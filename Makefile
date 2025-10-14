APPS = accounts instructors students surveys

.PHONY: test-unit test-all test-ft

test-unit:
	python src/manage.py test $(APPS)

test-ft:
	python src/manage.py test functional_tests

test-all:
	python src/manage.py test $(APPS) functional_tests