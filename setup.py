from setuptools import setup

setup(name='re_search',
	  version='0.1',
	  description='Tool/Package to search files with reqular expressions',
	  author='Tim Fischer',
	  author_email='tim.fischer98@hotmail.com',
	  license='MIT',
	  packages=['re_search'],
	  zip_safe=False,
	  entry_points={
	  	'console_scripts': ['search=re_search:Main'],
	  },)