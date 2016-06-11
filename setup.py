from setuptools import setup

setup(name='pyre-fsearch',
	  version='0.1',
	  description='Tool/Package to search files with reqular expressions',
	  author='Tim Fischer',
	  author_email='tim.fischer98@hotmail.com',
	  license='MIT',
	  packages=['pyre_fsearch'],
	  zip_safe=False,
	  entry_points={
	  	'console_scripts': ['research=pyre_fsearch:Main'],
	  },)
