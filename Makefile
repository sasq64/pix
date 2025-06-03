
all :
	mkdir -p build
	cmake -S . -B build -GNinja -DPYTHON_MODULE=ON -DCMAKE_BUILD_TYPE=Release
	ninja -C build _pixpy
	cp build/_pixpy*.so python/pixpy/

dist: stubs
	python -m build

run: all
	PYTHONPATH=build python3 test.py


mkdoc:
	python gendoc.py > docs/reference.md
	pandoc docs/reference.md -t asciidoc --shift-heading-level-by=-1 -o temp.adoc
	echo "= PIXPY" > .temp
	echo ":toc: left" >> .temp
	echo ":toclevels: 5" >> .temp
	echo ":source-highlighter: rouge" >> .temp
	echo "" >> .temp
	cat .temp temp.adoc > docs/reference.adoc
	asciidoctor -a docinfo=shared docs/reference.adoc


stubs: all 
	find python -name \*.pyi -exec rm {} \;
	PYTHONPATH=python pybind11-stubgen pixpy
	cp -a stubs/pixpy/_pixpy/* python/pixpy/
	python3 ./stubfix.py
	rm -rf stubs


