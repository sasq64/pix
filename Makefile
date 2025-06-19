
all :
	mkdir -p build
	cmake -S . -B build -GNinja -DPYTHON_MODULE=ON -DCMAKE_BUILD_TYPE=Debug
	ninja -C build _pixpy
	cp build/_pixpy*.so python/pixpy/

.PHONY: dist

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

patch:
	rm -rf unzt
	unzip dist/pixpy-0.1.15-cp313-cp313-macosx_15_0_arm64.whl -d unzt
	cp build/_pixpy.cpython-313-darwin.so unzt/pixpy/
	rm -f .dist/pixpy-0.1.15-cp313-cp313-macosx_15_0_arm64-debug.whl
	(cd unzt ; zip -r ../dist/pixpy-0.1.15-cp313-cp313-macosx_15_0_arm64-debug.whl *)


stubs: all 
	find python -name \*.pyi -exec rm {} \;
	PYTHONPATH=python pybind11-stubgen pixpy
	cp -a stubs/pixpy/_pixpy/* python/pixpy/
	python3 ./stubfix.py
	rm -rf stubs


