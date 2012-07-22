SHELL = /bin/sh

PROJECT='wardrobe'
ROOT_DIR=`pwd`

develop:
	if [ ! -f lib/buildout/bootstrap.py ]; then \
	    mkdir -p lib/buildout; \
	    wget http://svn.zope.org/*checkout*/zc.buildout/tags/1.5.2/bootstrap/bootstrap.py?content-type=text%2Fplain -O lib/buildout/bootstrap.py; \
	    python lib/buildout/bootstrap.py --distribute -c etc/buildout.cfg buildout:directory=${ROOT_DIR}; \
	fi
	bin/buildout -N -c etc/buildout.cfg buildout:directory=${ROOT_DIR}

update: develop

uninstall:
	rm -r bin/ lib/

tests:
	bin/nosetests --config=etc/nose.cfg

benchmark:
	bin/bpython benchmarks/stackeddict.py

documentation:
	rm -rf docs/api/generated/*
	bin/sphinx-autogen --output-dir=docs/api/generated/ --suffix=txt --templates=docs/_templates/ docs/api/index.txt
	bin/sphinx-autogen --output-dir=docs/api/generated/ --suffix=txt --templates=docs/_templates/ docs/api/generated/*.txt
	make --directory=docs clean html doctest

readme:
	mkdir -p docs/_build/html
	bin/rst2 html README.rst > docs/_build/html/README.html

release:
	bin/fullrelease
