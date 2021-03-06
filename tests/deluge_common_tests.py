#encoding: utf-8
""" Deluge test env init utilities """
import tempfile

import deluge.configmanager
import deluge.log

deluge.log.setupLogger("none")

def set_tmp_config_dir():
	""" initialize temp deluge env """
	config_directory = tempfile.mkdtemp()
	deluge.configmanager.set_config_dir(config_directory)
	return config_directory

def restore_config_dir():
	""" restore temp deluge env """
	config_directory = deluge.common.get_default_config_dir()
	deluge.configmanager.set_config_dir(config_directory)

import gettext
import locale
import pkg_resources

# Initialize gettext
try:
	locale.setlocale(locale.LC_ALL, '')
	if hasattr(locale, "bindtextdomain"):
		#pylint: disable=E1101
		locale.bindtextdomain("deluge", \
				pkg_resources.resource_filename("deluge", "i18n"))
	if hasattr(locale, "textdomain"):
		locale.textdomain("deluge")
		#pylint: disable=E1101
		gettext.bindtextdomain("deluge", \
				pkg_resources.resource_filename("deluge", "i18n"))
		gettext.textdomain("deluge")
		#pylint: disable=E1101
		gettext.install("deluge", pkg_resources.resource_filename("deluge", "i18n"))
except Exception, exc:
	print exc

