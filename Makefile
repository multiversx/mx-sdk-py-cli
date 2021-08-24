clean:
	rm -rf ./dist

build-erdpy: clean
	python3 setup.py sdist

publish-erdpy: build-erdpy
	twine upload dist/*

test:
	python3 -m unittest discover -s erdpy/tests
	pytest ./erdpy/tests/test_testnet.py -s
	source ./erdpy/tests/test_cli_all.sh && testAll || return 1
