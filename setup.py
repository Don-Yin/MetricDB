from setuptools import setup, find_packages

setup(
    name="MetricDB",
    version="0.0.2",
    author="Don Yin",
    author_email="Don_Yin@outlook.com",
    description="A logger based on SQLite3",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Don-Yin/MetricDB",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.12",
)
