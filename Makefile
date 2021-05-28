clean:
	rm -rf ./dist

build-erdpy: clean
	python3 setup.py sdist

publish-erdpy: build-erdpy
	twine upload dist/*
