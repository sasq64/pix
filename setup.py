from skbuild import setup
debug = False
mode = "-DCMAKE_BUILD_TYPE=Debug" if debug else "-DCMAKE_BUILD_TYPE=Release"
setup(
    name="pixpy",
    version="0.1.14",
    packages=["pixpy"],  # , "pixpy.color", "pixpy.event", "pixpy.key"],
    package_dir={"": "python"},
    cmake_install_dir="python/pixpy",
    cmake_args=["--no-warn-unused-cli", mode, "-DPYTHON_MODULE=ON",
                "-DMACOSX_DEPLOYMENT_TARGET=10.15"],
    package_data={"pixpy": ["*.py", "**/*.py",
                            "py.typed", "*.pyi", "**/*.pyi", "*/*/*.pyi"]},
    zip_safe=False,
)
