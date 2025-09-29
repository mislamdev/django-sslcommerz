#!/usr/bin/env python
"""
Setup configuration for django-sslcommerz package.
"""
from setuptools import setup, find_packages
import os


# Read the README file
def read_file(filename):
    with open(os.path.join(os.path.dirname(__file__), filename), encoding="utf-8") as f:
        return f.read()


setup(
    name="django-sslcommerz",
    version="1.0.0",
    description="Django integration package for SSLCOMMERZ Payment Gateway API v4",
    long_description=read_file("README.md"),
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/django-sslcommerz",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "Django>=3.2",
        "requests>=2.25.0",
        "python-decouple>=3.4",
    ],
    extras_require={
        "drf": ["djangorestframework>=3.12.0"],
        "dev": [
            "pytest>=6.0.0",
            "pytest-django>=4.0.0",
            "pytest-cov>=2.0.0",
            "black>=21.0.0",
            "flake8>=3.8.0",
            "isort>=5.0.0",
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Framework :: Django :: 3.2",
        "Framework :: Django :: 4.0",
        "Framework :: Django :: 4.1",
        "Framework :: Django :: 4.2",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    keywords="django sslcommerz payment gateway bangladesh",
)
