from setuptools import find_packages
from setuptools import setup

MAJOR_VERSION = '0'
MINOR_VERSION = '0'
MICRO_VERSION = '0'
VERSION = "{}.{}.{}".format(MAJOR_VERSION, MINOR_VERSION, MICRO_VERSION)

setup(
    name='nostalgia',
    version=VERSION,
    description="oops",
    url='https://github.com/kootenpv/nostalgia',
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
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
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
        # "lxml",  # web_history
        # "diskcache",  # web_history
        # "auto_extract",  # web_history
        # "ujson",  # web_history
        # "google-api-python-client",  # offers
        # "python-dotenv",  # offers
        # "natura",  # offers
    ],
    zip_safe=False,
    platforms='any',
)
