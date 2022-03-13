from pathlib import Path
from setuptools import setup, find_packages  # type: ignore[import]

reqs = Path("requirements.txt").read_text().splitlines()

setup(
    name="budget",
    version="0.1.0",
    url="https://github.com/seanbreckenridge/mint",
    author="Sean Breckenridge",
    author_email="seanbrecke@gmail.com",
    description=("""code to interact with/visualize mintable exports"""),
    license="MIT",
    packages=find_packages(include=["budget"]),
    install_requires=reqs,
    entry_points={"console_scripts": ["budget = budget.__main__:main"]},
    keywords="money finances data",
    extras_require={
        "graphs": [
            "scipy",
            "matplotlib",
        ],
    },
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
)
