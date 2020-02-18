# Encoding: utf-8

from setuptools import setup, find_packages


setup(
    name='py-imap-to-http',
    version='0.1',
    packages=find_packages(),
    install_requires=(
        'aioimaplib',
        'mail-parser',
        'requests',
        'requests-toolbelt',
    ),
    extras_require={
        'dotenv': (
            'python-dotenv'
        ),
        'test': (
            'mock',
            'flake8',
            'pytest',
            'pytest-sugar',
            'coverage',
        ),
    },
)
