from setuptools import find_packages
from setuptools import setup

with open("README.md") as f:
    LONG_DESCRIPTION = f.read()

MAJOR_VERSION = "0"
MINOR_VERSION = "1"
MICRO_VERSION = "42"
VERSION = "{}.{}.{}".format(MAJOR_VERSION, MINOR_VERSION, MICRO_VERSION)

setup(
    name='nostalgia',
    version=VERSION,
    description="nostalgia enables to self-track and gain insights into your life",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url='https://github.com/nostalgia-dev/nostalgia',
    author='Pascal van Kooten',
    author_email='kootenpv@gmail.com',
    license='MIT',
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Customer Service',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: Microsoft',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Unix',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Software Development',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Debuggers',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Software Distribution',
        'Topic :: System :: Systems Administration',
        'Topic :: Utilities',
    ],
    install_requires=[
        "just",
        "pandas",
        "metadate",
        "tok",
        "ijson",
        "cython",
        "pyarrow",
        "tldextract",
        "diskcache",
        "tzlocal",
        # "lxml",  # web_history
        # "diskcache",  # web_history
        # "auto_extract",  # web_history
        # "ujson",  # web_history
        # "google-api-python-client",  # offers
        # "python-dotenv",  # offers
        # "natura",  # offers
    ],
    package_data={
        # If any package contains *.txt or *.rst files, include them:
        # '': ['*.txt', '*.rst'],
        "nostalgia": ["**/*.parquet"]
    },
    zip_safe=False,
    platforms='any',
)
