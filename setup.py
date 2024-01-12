from skbuild import setup
setup(
    name="pixpy",
    version="0.1.11",
    packages=["pixpy"], #, "pixpy.color", "pixpy.event", "pixpy.key"],
    package_dir={"": "python"},
    cmake_install_dir="python/pixpy",
    cmake_args=["--no-warn-unused-cli", "-DPYTHON_MODULE=ON", "-DMACOSX_DEPLOYMENT_TARGET=10.15"],
    package_data={"pixpy": ["*.py", "**/*.py", "py.typed", "*.pyi", "**/*.pyi", "*/*/*.pyi"]},
    zip_safe=False,
)
