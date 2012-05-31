#! /bin/sh 

export PATH="$PATH:./bash"
#python -m unittest discover
trial -r gtk2 test*.py

