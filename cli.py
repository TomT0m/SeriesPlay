#! /usr/bin/python2.6

import subprocess
import os

class FileNameError(Exception):
     def __init__(self, value):
         self.value = value
     def __str__(self):
         return repr(self.value)

class command_executer:
        def get_output(self, cmd, working_dir=None):
        #       print(cmd)
        #       print("rep :",working_dir)
                if working_dir!=None and not os.path.exists(working_dir) :
                        raise FileNameError(working_dir)
                p = subprocess.Popen(cmd, shell=False, bufsize=0, stdout=subprocess.PIPE, cwd=working_dir ).communicate()[0]
        #       p = subprocess.Popen(cmd, shell=False, bufsize=0, stdout=subprocess.PIPE  ).communicate()[0]
        #       print(type(p),":",p)
                # p=p.decode("utf-8")
        #       print(type(p),":",p)
                return p

        def get_list_output(self,cmd,separator='\n',cwd=None):
                print("working rep:",cwd)
                return self.get_output(cmd,cwd).split(separator)

class command_line_generator:
        def __init__(self,command):
                self.command=[command]

        def add_option_single(self,option):
                self.command.append(option)

        def get_command(self):
                return self.command

        def add_option_param(self,name,val):
                self.command.append(name)
                self.command.append(val)

class config_manager:
	def __init__(self,config_file_name):
		self.config_file_name=config_file_name

	def read_var(self,var_name):
		return self.read_conf_var(self.config_file_name,var_name)

	
	def write_var(self,var_name,value):
		return self.write_conf_var(self.config_file_name,var_name,value)

	def read_num_var(self,var_name):
		return self.read_num_conf_var(self.config_file_name,var_name)

# config management 

	@classmethod
        def read_conf_var(cls,config_file_path,var_name):
		executer=command_executer()
                # print(config_file_path.decode(utf-8))
                if os.path.exists(config_file_path):
                        return executer.get_output(["get_conf_variable_val",config_file_path,var_name])
                else:
                        raise FileNameError(config_file_path)

                        # return None
	@classmethod
        def write_conf_var(cls,config_file_path,var_name,value):
		executer=command_executer()
                if os.path.exists(config_file_path):
                        return executer.get_output(["set_conf_variable_val",config_file_path,var_name,value])
                else:
                        raise FileNameError(config_file_path)

        @classmethod
        def read_num_conf_var(self,config_file_path,var_name):
                print("reading conf var")

                try:
                        res=self.read_conf_var(config_file_path,var_name)
                        print(res)
                        num = int( self.read_conf_var(config_file_path,var_name))
                        print(type(num),num)
                        return num
                except  ValueError :
                        print(None)
                        return None


if __name__ == "__main__":
	print("Put here the unit tests ...")

