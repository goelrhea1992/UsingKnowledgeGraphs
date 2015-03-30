#!/bin/bash

if [ "$#" -ne 2 ] && [ "$#" -ne 6 ]; then
    echo "Illegal number of parameters"
fi

if [ "$#" -eq 6 ]; then
	python InfoBox.py "-$1" $2 $3 "'$4'" $5 $6
else if [ "$#" -eq 2 ]; then
		python InfoBox.py "-$1" $2
	fi
fi

