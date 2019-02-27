#!/usr/bin/env python3
'''
Setup for pyfos
'''
from setuptools import setup, find_packages

setup(
	name='pyfos',
	version='1.1.1',
	description='Brocade FOS Library.',
	author='Brocade Communications Systems LLC.',
	author_email='Automation.BSN@broadcom.com',
	url='http://www.brocade.com/',
	install_requires=['openpyxl', 'colorconsole', 'xlrd', 'jsondiff', 'requests', 'xmltodict'],
	packages=find_packages()
)
