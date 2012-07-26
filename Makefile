SHELL = /bin/sh

PROJECT = 'wardrobe'
ROOT_DIR = `cd $(@D) && pwd`
DATA_DIR = $(ROOT_DIR)/var


buildout:
	if [ ! -f lib/buildout/bootstrap.py ]; then \
	    mkdir -p lib/buildout; \
	    wget http://svn.zope.org/*checkout*/zc.buildout/tags/1.5.2/bootstrap/bootstrap.py?content-type=text%2Fplain -O lib/buildout/bootstrap.py; \
	    python lib/buildout/bootstrap.py --distribute -c etc/buildout.cfg buildout:directory=${ROOT_DIR}; \
	fi
	bin/buildout -N -c etc/buildout.cfg buildout:directory=${ROOT_DIR}

develop: buildout

update: develop

clean:
	rm -rf $(ROOT_DIR)/bin/ $(ROOT_DIR)/lib/

test:
	bin/nosetests --config=etc/nose.cfg

benchmark:
	bin/bpython benchmarks/stackeddict.py

documentation:
	# Generate API documentation, under version control.
	rm -rf docs/api/generated/*
	bin/sphinx-autogen --output-dir=docs/api/generated/ --suffix=txt --templates=docs/_templates/ docs/api/index.txt
	bin/sphinx-autogen --output-dir=docs/api/generated/ --suffix=txt --templates=docs/_templates/ docs/api/generated/*.txt
	# Build the documentation.
	make --directory=docs clean html doctest

readme:
	mkdir -p $(DATA_DIR)/docs/html
	bin/rst2 html README > $(DATA_DIR)/docs/html/README.html

release:
	bin/fullrelease
