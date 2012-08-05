#! /bin/bash 

export PATH="$PATH:./bash"

cd ..

#python -m unittest discover
#echo $# ; exit


if [ "$#" == "0" ] ; then
	trial -r gi tests/test*.py
else
	tests=("$@")
	args=()
	for index in ${!tests[*]}; do
		args[$index]="tests/${tests[$index]}"
	done
	trial -r gi "${args[@]}"
fi
