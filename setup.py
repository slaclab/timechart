import versioneer
from setuptools import setup, find_packages

setup(
    name='pydmcharting',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    # Author details
    author='SLAC National Accelerator Laboratory',

    packages=find_packages(),
    package_dir={'pydmcharting':'pydmcharting'},
    description='Python Display Manager Charting Tool',
    url='https://github.com/slaclab/pydmcharting',
    entry_points={
        'gui_scripts': [
            'pydmcharting=pydmcharting.main:main'
        ]
    },
    license='BSD',
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
