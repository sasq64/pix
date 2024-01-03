
all :
	mkdir -p build
	cmake -S . -B build -GNinja -DBUILD_PIXPY=1 -DCMAKE_BUILD_TYPE=Release
	ninja -C build _pixpy

run:
	PYTHONPATH=build python3 test.py

go:
	PYTHONPATH=cmake-build-debug python3 test.py


PYI0 = python/pixpy/__init__.pyi

stubs: all
	find python -name \*.pyi -exec rm {} \;
	PYTHONPATH=python pybind11-stubgen pixpy
	cp -a stubs/pixpy-stubs/_pixpy/* python/pixpy/
	python3 ./stubfix.py

	# echo 'from typing import Union, Tuple' | cat - $(PYI0) > temp && mv temp $(PYI0)
	# gsed -i 's/os.PathLike/str/g' $(PYI0)
	# gsed -i 's/import os/import os\nimport pixpy.color as color\nimport pixpy.event as event\nimport pixpy.key as key\n/g' $(PYI0)
	# gsed -i 's/: Float2/:Union[Float2, Tuple[float,float]]/g' $(PYI0)
	# gsed -i 's/: Int2/:Union[Int2, Tuple[int, int]]/g' $(PYI0)
	# gsed -i 's/pixpy\._pixpy\.//g' $(PYI0)
	# gsed -i 's/class AnyEvent():/class __IgnoreMeReallyShouldBeDeleted():/' python/pixpy/event/__init__.pyi
	# gsed -i 's/\._pixpy//g'  python/pixpy/event/__init__.pyi
	# gsed -i 's/import typing/import typing\nimport pixpy/'  python/pixpy/event/__init__.pyi
	# echo 'AnyEvent = typing.Union[NoEvent, Key, Move, Click, Text, Resize, Quit]' >>  python/pixpy/event/__init__.pyi
