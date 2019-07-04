from setuptools import setup


def readme():
    with open("README.md") as f:
        return f.read()
        
setup(name='biclustpy',
      version='0.2',
      description='bi-cluster editing library',
      long_description=readme(),
      long_description_content_type='text/markdown',
      keywords='bi-cluster editing',
      url='http://github.com/dbblumenthal/biclustpy',
      author='David B. Blumenthal',
      author_email='david.blumenthal@wzw.tum.de',
      license='LGPL',
      packages=['biclustpy'],
      install_requires=[
          'numpy',
          'argparse',
          'networkx',
          'progress',
          'gurobipy'
      ],
      entry_points={
          'console_scripts': ['biclustpy=biclustpy.command_line:main'],
      },
      include_package_data=True,
      zip_safe=False)
