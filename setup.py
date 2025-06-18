from setuptools import setup, find_packages
import pathlib

BASE_DIR = pathlib.Path(__file__).parent

with open(BASE_DIR / 'README.md', encoding='utf-8') as f:
    long_description = f.read()


def parse_requirements(path: str):
    reqs = []
    with open(BASE_DIR / path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                reqs.append(line)
    return reqs

setup(
    name='dash-csrf-plugin',
    version='0.1.0',
    description='CSRF protection plugin for Dash applications',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(exclude=('tests*', 'examples*')),
    install_requires=parse_requirements('requirements.txt'),
    entry_points={'console_scripts': ['dash-csrf-plugin=dash_csrf_plugin.cli:cli']},
    python_requires='>=3.8',
)
