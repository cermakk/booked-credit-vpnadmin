import os
import subprocess
from setuptools import setup, find_packages
from setuptools.command.install import install


class MyInstall(install):
    def run(self):
        projpath = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                'creditbased-vpnadmin')
        print 'Generating MO files in %s' % projpath
        subprocess.call(['django-admin.py', 'compilemessages'],
                        cwd=projpath)
        install.run(self)

setup(
    name='creditbased-vpnadmin',
    version='0.1',
    description='T-mobile VPN network admin.',
    author='KC',
    author_email='',
    url='',
    packages=find_packages(),
    include_package_data=True,
    cmdclass={'install': MyInstall},
)
