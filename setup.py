import versioneer
from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().split()

git_requirements = [r for r in requirements if r.startswith('git+')]
requirements = [r for r in requirements if not r.startswith('git+')]

if len(git_requirements) > 0:
    print("User must install \n" +
          "\n".join('{}'.format(r) for r in git_requirements) +
          "\n\nmanually")


setup(
    name="timechart",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    author="SLAC National Accelerator Laboratory",
    packages=find_packages(),
    package_dir={"timechart": "timechart", "timechart_launcher": "timechart_launcher"},
    description="Time Chart Tool based on PyDM",
    url="https://github.com/slaclab/timechart",
    entry_points={
        "gui_scripts": ["timechart=timechart_launcher.main:main"],
        "pydm.tool": [
            "timechart=timechart.tool:PydmTimeChartTool",
        ],
    },
    license="BSD",
    include_package_data=True,
    classifiers=[
        "License :: OSI Approved :: BSD License",
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    install_requires=requirements,
)
