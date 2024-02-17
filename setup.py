from setuptools import setup, find_packages
import os
import re
import shutil
import sys

def get_version(package):
    """
    Return package version as listed in `__version__` in `init.py`.
    """
    init_py = open(os.path.join(package, '__init__.py')).read()
    return re.search("__version__ = ['\"]([^'\"]+)['\"]", init_py).group(1)


version = get_version('dock_craftsman')

if sys.argv[-1] == 'publish':
    os.system("python setup.py sdist bdist_wheel")
    if os.system("twine check dist/*"):
        print("twine check failed. Packages might be outdated.")
        print("Try using `pip install -U twine wheel`.\nExiting.")
        sys.exit()
    os.system("twine upload dist/*")
    # print("You probably want to also tag the version now:")
    # print("  git tag -a %s -m 'version %s'" % (version, version))
    # print("  git push --tags")
    shutil.rmtree('dist')
    shutil.rmtree('build')
    shutil.rmtree('dock_craftsman.egg-info')
    sys.exit()
    
def read(f):
    with open(f, 'r', encoding='utf-8') as file:
        return file.read()
    
setup(
    # Package metadata
    name='dock-craftsman',
    version='0.0.11',
    url='https://dock-craftsman.code4mk.org/',
    author='Mostafa Kamal',
    author_email='hiremostafa@gmail.com',
    description='docker',
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    keywords=['docker'],
    
    # Package configuration
    packages=find_packages(exclude=['tests*', 'template*']),
    
    # Dependencies
    install_requires=[
        'docker==7.0.0',
        'rich==13.7.0',
    ],

    # Classifiers
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    project_urls={
        'Source': 'https://github.com/code4mk/dock-craftsman',
        'Changelog': 'https://github.com/code4mk/dock-craftsman',
    },
)
