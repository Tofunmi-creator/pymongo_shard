from setuptools import setup
setup(name='pymongo_shard',
      version='0.1.1',
      description ='A package to extract data via API requuests from server shards (endpoints) running pymongo, the official Python MongoDB driver.',
      packages=['pymongo_shard'],
      python_requires='>=3.11, !=4.0.*',
      install_requires = [
                          'pymongo>=4.15.1',
                          'psutil>=7.1.0',
                          ],
      author = 'Oluwatofunmi Caulcrick',
      author_email='johncaul@yahoo.com',
      zip_safe=False,
)