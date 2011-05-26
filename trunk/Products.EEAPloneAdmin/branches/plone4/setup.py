from setuptools import setup, find_packages
import os
from os.path import join

name = 'Products.EEAPloneAdmin'
path = name.split('.') + ['version.txt']
version = open(join(*path)).read().strip()

setup(name=name,
      version=version,
      description="EEA Plone Admin",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='eea',
      author='European Environment Agency (EEA)',
      author_email='webadmin@eea.europa.eu',
      url='http://svn.eionet.europa.eu/projects/Zope/browser/trunk/Products.EEAPloneAdmin',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-

          'Products.LinguaPlone',
          'Products.PloneHelpCenter',

          'eea.translations',
          'Products.NavigationManager',
          'valentine.linguaflow',

          #used in testing
          'eea.themecentre',

          #plone4: disabled during migration
          #'eea.mediacentre',
          #'eea.reports',

      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
