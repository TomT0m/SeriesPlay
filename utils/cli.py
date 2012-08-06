#! /usr/bin/python
#encoding: utf-8
""" Helper classes and function for handling command line interface commands"""

import subprocess
import os

from logging import debug, info

class FileNameError(Exception):
	""" Exception thrown when command does not exists """
	def __init__(self, value):
		Exception.__init__(value)
		self.value = value
	     
	def __str__(self):
		return repr(self.value)

# class CommandException(Exception):
# 	pass	

class CommandExecuter(object):
	""" Encapsulates a command execution """
        
	def get_output(self, cmd, working_dir=None):
		""" executes a command and gets the standard output """
		if working_dir != None and not os.path.exists(working_dir) :
		
			raise FileNameError(working_dir)
		try:
			process = subprocess.Popen(cmd, shell=False, 
					bufsize=0, stdout=subprocess.PIPE, 
					cwd=working_dir )\
							.communicate()[0]
		except OSError as (perror, msg): #pylint: disable=W0623
			debug("Error executing {0} perr : {} msg :{}".format(cmd, perror, msg))
			raise
		except child_exception: #pylint: disable=E0602 
			print "Error executing {0}".format(cmd)
			raise	
		return process

	def get_list_output(self, cmd, separator='\n', cwd=None):
		""" returns a list of string, the output of the "cmd" command
		"""
		debug("working rep:", cwd)
		return self.get_output(cmd, cwd).split(separator)

class CommandLineGenerator(object):
	""" command line with argument generator """

	def __init__(self, command):
		self.command = [command]

	def add_option_single(self, option):
		""" adds a single switch """
		self.command.append(option)

	def get_command(self):
		""" getter to the command """ 
		return self.command

	def add_option_param(self, name, val):
		""" adds a pair arg, value to the command"""
		self.command.append(name)
		self.command.append(val)

class ConfigManager:
	""" A config object, associated with a conf file """
	def __init__(self, config_file_name):
		self.config_file_name = config_file_name

	def read_var(self, var_name):
		""" Returns the value of var_name in this config """
		return self.read_conf_var(self.config_file_name, var_name)

	
	def write_var(self, var_name, value):
		""" Sets and write the value of var_name in this config """
		return self.write_conf_var(self.config_file_name, var_name, value)

	def read_num_var(self, var_name):
		""" Returns the value of integer var_name in this config """
		return self.read_num_conf_var(self.config_file_name, var_name)

# config management and storage 

	@classmethod
	def read_conf_var(cls, config_file_path, var_name):
		""" wrapper for reading a conf var in a file (VAR_NAME=VALUE)
		returns VALUE
		TODO: rewrite in python
		"""
		executer = CommandExecuter()
		# print(config_file_path.decode(utf-8))
		if os.path.exists(config_file_path):
			return executer.get_output(
					["get_conf_variable_val", config_file_path, var_name])
		else:
			raise FileNameError(config_file_path)
	
	@classmethod
	def write_conf_var(cls, config_file_path, var_name, value):
		""" wrapper for settind a conf var in a file (format VAR_NAME=VALUE)
		TODO: rewrite in python
		"""
		executer = CommandExecuter()
		if os.path.exists(config_file_path):
			return executer.get_output(
					["set_conf_variable_val", 
						config_file_path,
						var_name,
						value])
		else:
			raise FileNameError(config_file_path)

	@classmethod
	def read_num_conf_var(cls, config_file_path, var_name):
		""" Reads a numeric var in a file """
		info("reading conf var")

		try:
			res = cls.read_conf_var(config_file_path, var_name)
			debug(res)
			num = int( cls.read_conf_var(config_file_path, var_name))
			debug("Value read", type(num), num)
			return num
		except ValueError :
			debug("not an int" )
			return None


if __name__ == "__main__":
	print("Put here the unit tests ...")

