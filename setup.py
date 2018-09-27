import versioneer
from setuptools import setup, find_packages

setup(
    name='timechart',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    # Author details
    author='SLAC National Accelerator Laboratory',

    packages=find_packages(),
    package_dir={'timechart':'timechart', 'timechart_launcher':'timechart_launcher'},
    description='Time Chart Tool based on PyDM',
    url='https://github.com/slaclab/timechart',
    entry_points={
        'gui_scripts': [
            'timechart=timechart_launcher.main:main'
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
