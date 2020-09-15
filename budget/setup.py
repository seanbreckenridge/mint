from setuptools import setup, find_packages

requirements = [
    "logzero",
    "click",
    "IPython",
    "more-itertools",
    "gitpython",
    "pick",
    "pyfiglet",
    "pandas",
    "vimbuffer",
]

setup(
    name="budget",
    version="0.1.0",
    url="https://github.com/seanbreckenridge/mint",
    author="Sean Breckenridge",
    author_email="seanbrecke@gmail.com",
    description=("""code to interact with/visualize mintable exports"""),
    license="MIT",
    packages=find_packages(include=["budget"]),
    install_requires=requirements,
    keywords="reddit data",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
)
