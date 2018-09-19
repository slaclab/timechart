from setuptools import setup, find_packages

# To use a consistent encoding
from codecs import open
from os import path, environ

cur_dir = path.abspath(path.dirname(__file__))

with open(path.join(cur_dir, 'requirements.txt')) as f:
    requirements = f.read().split()

setup(
    name='pydmcharting',
    version="1.0.0",
    # Author details
    author='SLAC National Accelerator Laboratory',

    packages=find_packages(),
    package_dir={'pydmcharting':'pydmcharting'},
    description='Python Display Manager Charting Tool',
    url='https://github.com/hmbui/pydmcharting',
    entry_points={
        'gui_scripts': [
            'pydmcharting=pydmcharting.main:main'
        ]
    },
    license='BSD',

    install_requires=requirements,
    include_package_data=True,
    classifiers=[
        'License :: OSI Approved :: BSD License',
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ]
)
