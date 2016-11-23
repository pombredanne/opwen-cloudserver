from setuptools import find_packages
from setuptools import setup


with open('requirements.txt') as fobj:
    install_requires = [line.strip() for line in fobj]


with open('README.rst') as fobj:
    long_description = fobj.read()


packages = find_packages(exclude=['tests*'])


setup(
    name='opwen_email_server',
    version='0.0.4',
    author='Clemens Wolff',
    author_email='clemens.wolff+pypi@gmail.com',
    packages=packages,
    url='https://github.com/OPWEN/opwen-cloudserver',
    license='LICENSE.txt',
    description='Email server for the Opwen project',
    long_description=long_description,
    install_requires=install_requires)
