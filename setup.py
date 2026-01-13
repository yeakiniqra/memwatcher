"""
Setup configuration for memwatcher
"""
from setuptools import setup, find_packages
from pathlib import Path

# Read the long description from README
this_directory = Path(__file__).parent
long_description = ""
readme_path = this_directory / "README.md"
if readme_path.exists():
    long_description = readme_path.read_text(encoding='utf-8')

setup(
    name='memwatcher',
    version='0.1.0',
    description='Intelligent Memory Leak Detective for Python',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Yeakin Iqra',
    author_email='yeakintheiqra@gmail.com',
    url='https://github.com/yeakiniqra/memwatcher',
    license='MIT',
    
    packages=find_packages(exclude=['tests', 'tests.*', 'examples']),
    
    python_requires='>=3.7',
    
    install_requires=[
        'psutil>=5.8.0',
    ],
    
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-cov>=3.0.0',
            'black>=22.0.0',
            'flake8>=4.0.0',
            'mypy>=0.950',
        ],
        'django': [
            'django>=3.2',
        ],
        'fastapi': [
            'fastapi>=0.68.0',
        ],
    },
    
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Monitoring',
        'Topic :: Software Development :: Debuggers',
    ],
    
    keywords='memory leak detection monitoring profiling debugging',
    
    project_urls={
        'Bug Reports': 'https://github.com/yeakiniqra/memwatcher/issues',
        'Source': 'https://github.com/yeakiniqra/memwatcher',
        'Documentation': 'https://memwatcher.readthedocs.io',
    },
    
    entry_points={
        'console_scripts': [
            'memwatcher=memwatcher.cli:main',
        ],
    },
)