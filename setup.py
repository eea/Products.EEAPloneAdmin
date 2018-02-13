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
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
          "Framework :: Zope2",
          "Framework :: Plone",
          "Framework :: Plone :: 4.0",
          "Framework :: Plone :: 4.1",
          "Framework :: Plone :: 4.2",
          "Framework :: Plone :: 4.3",
          "Programming Language :: Zope",
          "Programming Language :: Python",
          "Programming Language :: Python :: 2.7",
          "Topic :: Software Development :: Libraries :: Python Modules",
          "License :: OSI Approved :: GNU General Public License (GPL)",
      ],
      keywords='EEA Add-ons Plone Zope',
      author='European Environment Agency: IDM2 A-Team',
      author_email='eea-edw-a-team-alerts@googlegroups.com',
      url='https://github.com/eea/Products.EEAPloneAdmin',
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
          'ftw.globalstatusmessage',

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
