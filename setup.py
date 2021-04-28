"""
setup.py for life-exam
Usage: sudo pip3 install .
"""
__author__ = 'Thomas Michael Weissel'

from distutils.core import setup
from version import __version__

if __name__ == '__main__':

    setup(
        name="life-builder",
        version=__version__,
        description="a LiFE Tool",
        author=__author__,
        maintainer=__author__,
        license="GPLv3",
        author_email="valueerror@gmail.com",
        url="http://life-edu.eu",
        install_requires=[
            'ConfigObj'
        ],
        python_requires='>=3.8',
    )
