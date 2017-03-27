""" EEA Plone Admin installer
"""
import os
from os.path import join
from setuptools import setup, find_packages

name = 'Products.EEAPloneAdmin'
path = name.split('.') + ['version.txt']
version = open(join(*path)).read().strip()

setup(name=name,
      version=version,
      description="EEA Plone Admin",
      long_description=open("README.rst").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='eea',
      author='European Environment Agency (EEA)',
      author_email='webadmin@eea.europa.eu',
      url='http://svn.eionet.europa.eu/projects/'
          'Zope/browser/trunk/Products.EEAPloneAdmin',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'eventlet',
          'Products.LinguaPlone',
          'eea.translations',
          'Products.NavigationManager',
          'Products.contentmigration',
          'valentine.linguaflow',
          'collective.quickupload',
          'collective.deletepermission',

          # Used in testing
          'eea.themecentre',
          'eea.mediacentre',
          'eea.reports',
      ],
      extras_require={
          'yum': [
              'python-ldap'
              ],
          'apt': [
              'python-ldap'
          ]
      },
      entry_points="""
      # -*- entry_points -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
