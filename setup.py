"""My Libs install
python setup.py develop: install link (egg link) of my_libs to [current folder]/my_libs

python setup.py build: build
python setup.py install easy_install: Find/get/install Python packages

python setup.py sdist bdist_wheel: create wheel and tar.gz packages
    pip install --use-wheel --no-index --find-links=[folder contains whl file] my_libs

pip uninstall my_libs

Standard commands:
    build             build everything needed to install
    build_py          "build" pure Python modules (copy to build directory)
    build_ext         build C/C++ extensions (compile/link to build directory)
    build_clib        build C/C++ libraries used by Python extensions
    build_scripts     "build" scripts (copy and fixup #! line)
    clean             clean up temporary files from 'build' command
    install           install everything from build directory
    install_lib       install all Python modules (extensions and pure Python)
    install_headers   install C/C++ header files
    install_scripts   install scripts (Python or otherwise)
    install_data      install data files
    sdist             create a source distribution (tarball, zip file, etc.)
    register          register the distribution with the Python package index
    bdist             create a built (binary) distribution
    bdist_dumb        create a "dumb" built distribution
    bdist_rpm         create an RPM distribution
    bdist_wininst     create an executable installer for MS Windows
    upload            upload binary package to PyPI

Extra commands:
    rotate            delete older distributions, keeping N newest files
    develop           install package in 'development mode'
    setopt            set an option in setup.cfg or another config file
    saveopts          save supplied options to setup.cfg or other config file
    egg_info          create a distribution's .egg-info directory
    upload_sphinx     Upload Sphinx documentation to PyPI
    install_egg_info  Install an .egg-info directory for the package
    alias             define a shortcut to invoke one or more commands
    easy_install      Find/get/install Python packages
    bdist_egg         create an "egg" distribution
    test              run unit tests after in-place build
    build_sphinx      Build Sphinx documentation

"""
from setuptools import setup

setup(
    name="my_lib",
    version="0.0.1",
    packages=["my_lib"],
    url="",
    license="",
    author="TueTT",
    author_email="",
    description="",
    install_requires=[
        "pathvalidate",
        "jsonschema",
        "colorama",
        "wget",
        "clint",
        "beautifulsoup4",
        ],
    zip_safe=False,
)
