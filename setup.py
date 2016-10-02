import os
from setuptools import find_packages
from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()

setup(name='cba-notes',
      version="0.0",
      description='Notes app based on CBA',
      long_description=README,
      classifiers=[
          'Environment :: Web Environment',
          'Framework :: Django',
          'License :: OSI Approved :: BSD License',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
      ],
      package_data={
          'notes': [
              'locale/*/LC_MESSAGES/*',
          ],
      },
      keywords='django web applications framework',
      author='Kai Diefenbach',
      author_email='kai.diefenbach@iqpp.de',
      url='http://www.iqpp.com',
      license='BSD',
      packages=find_packages(exclude=('tests*',)),
      include_package_data=True,
      zip_safe=False,
      dependency_links=["http://pypi.iqpp.de/"],
      install_requires=[
          'setuptools',
          'django-taggit',
          'django-markupfield',
          'Markdown',
      ],
)
