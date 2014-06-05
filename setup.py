from setuptools import setup, find_packages
import os

version = '1.0beta2'

setup(name='collective.flexibleordering',
      version=version,
      description="A custom folder ordering implementation, which stores order persistently, but sorts content based on a rule.",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='',
      author='Alec Mitchell',
      author_email='alecpm@gmail.com',
      url='http://github.com/jazkarta/collective.flexibleordering',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'blist',
      ],
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
