#!/usr/bin/python
#encoding:utf-8
""" Installer Setup config file"""

from distutils.core import setup

import glob

BASH_SCRIPTS = glob.glob("bash/*")

DESKTOP_DATA = 'ui/data/SeriesPlay.desktop'

DATA_FILES = [
	    ('/usr/share/icons/scalable/apps', ['ui/data/icons/scalable/apps/SeriesPlay.svg'])]
DATA_FILES.append(('/usr/share/applications', [DESKTOP_DATA]))

setup(
    name = 'SeriePlay',
    version = '1.0dev2',
    packages = ['datasource', 'ui', 'utils', \
		    'pysrt', 'gobj_player', \
		    'serie', 'tests', 'app'],
    scripts = ['ifaceplay','video_finder_server.py'] + BASH_SCRIPTS,
    license = 'WTFPL Version 2',
    description = 'TV series collection manager',
    install_requires = ['GObject >= 1.0', 'Gtk >= 3.0'],
    long_description=open('README').read(),
    package_data = { "ui" : ['*.ui']},
    data_files = DATA_FILES
)
