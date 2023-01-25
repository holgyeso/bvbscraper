from setuptools import find_packages, setup

setup(
    name='bvbscraper',
    packages=find_packages(include=["bvbscraper", "bvbscraper.bvb*"]),
    version='0.1.0',
    description='library to scrape BVB',
    author='Orsolya-Dorottya, Holgyes',
    license='MIT',
    install_requires=["requests", "beautifulsoup4", "uuid", "python-dateutil", "pandas"]
)