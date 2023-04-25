from setuptools import setup, find_packages
from src import BOT_VERSION

setup(
    name="BOT",
    version=BOT_VERSION,
    description="Tools for behavior-oriented software engineering methodology.",
    author="masol.lee",
    author_email="masol.li@gmail.com",
    packages=find_packages(),
    install_requires=[
        "click",
    ],
    entry_points={
        "console_scripts": [
            "bot = __main__:bot",
        ],
    },
)
