from distutils.core import setup

setup(
    name='chimera_domesync',
    version='0.0.1',
    packages=['chimera_domesync', 'chimera_domesync.util', 'chimera_domesync.instruments'],
    scripts=[],
    url='http://github.com/astroufsc/chimera-domesync',
    license='GPL v2',
    author='William Schoenell',
    author_email='william@astro.ufsc.br',
    description='Dome synchronization for chimera observatory control system'
)
