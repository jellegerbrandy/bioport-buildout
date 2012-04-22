# -*- coding: utf-8 -*-
"""
Integration of plone with bioport site skin
"""
import os
from setuptools import setup, find_packages

version = '6.0.6'

setup(name='inghist.bioporttheme',
      version=version,
      description=" 4.1",
#      long_description=open(os.path.join("inghist", "theme", "bioport", "README.txt")).read() + "\n\n" +
#                       open(os.path.join("docs", "INSTALL.txt")).read() + "\n\n"+
#                       open(os.path.join("docs", "HISTORY.txt")).read(),    
                                             
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        'Framework :: Plone',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],
      author='Jelle Gerbrandy',
      author_email='jelle@gerbrandy.com',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['inghist', 'inghist.theme',],
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        'plone.app.theming',
                        'plone.app.themingplugins',
                        ],
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
