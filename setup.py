#!/usr/bin/python
#encoding:utf-8

from distutils.core import setup

import glob

bash_scripts = glob.glob("bash/*")
print (bash_scripts)

setup(
    name='SeriePlay',
    version='1.0dev',
    packages=['datasource','ui','utils','pysrt','gobj_player','serie'],
    scripts=['ifaceplay','video_finder_server.py']+bash_scripts,
    license='WTFPL Version 2',
    description='TV series collection manager',
    install_requires=['GObject >= 1.0','Gtk >= 3.0'],
    long_description=open('README').read(),
    package_data = { "ui" : ['*.ui']} 
)
