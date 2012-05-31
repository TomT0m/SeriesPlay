#! /bin/bash 

export PATH="$PATH:./bash"

cd ..

#python -m unittest discover
#echo $# ; exit

if [ "$#" == "0" ] ; then
	trial -r gi tests/test*.py
else
	trial -r gi $@
fi
