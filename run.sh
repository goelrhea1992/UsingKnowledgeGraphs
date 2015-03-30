#!/bin/bash

if [ "$#" -ne 2 ] && [ "$#" -ne 5 ]; then
    echo "Illegal number of parameters"
fi

if [ "$5" == "infobox" ]; then
	python InfoBox.py $2 $3 "'$4'"
else if [ "$5" == "question" ]; then
	#call script for Part 2 here
fi

