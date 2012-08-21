#! /bin/bash 

export PATH="$PATH:./bash"

cd ..

tests_dir="tests/"

args=("$@")


if [ "$#" == "0" ] ; then
	trial -r gi "$tests_dir"/test*.py
else
	tests=("$@")
	args=()
	for index in ${!tests[*]}; do
		args[$index]="$tests_dir/${tests[$index]}"
	done
	trial -r gi "${args[@]}"
fi
