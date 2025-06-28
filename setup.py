#!/usr/bin/env python3
"""
Setup script for ScayNum
Advanced OSINT Tool by Scayar
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="scaynum",
    version="4.0.0",
    author="Scayar",
    author_email="Scayar.exe@gmail.com",
    description="Advanced OSINT Tool for educational purposes",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/Scayar/ScayNum",
    project_urls={
        "Bug Tracker": "https://github.com/Scayar/ScayNum/issues",
        "Documentation": "https://scayar.com",
        "Source Code": "https://github.com/Scayar/ScayNum",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Security",
        "Topic :: Internet :: WWW/HTTP :: Indexing/Search",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    packages=find_packages(),
    py_modules=["main"],
    include_package_data=True,
    install_requires=read_requirements(),
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "scaynum=main:main",
        ],
    },
    keywords="osint, intelligence, social media, phone lookup, ip lookup, web search",
    zip_safe=False,
) 