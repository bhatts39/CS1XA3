#!/bin/bash
printf "%s\n" "--Project 01--"
while true
do
	read command
	if [ $command == "filetypecount" ]; then
		declare -a types=( "html" "js" "css" "py" "hs" "sh" )
		for type in "${types[@]}"
		do
			count=$(find ~/CS1XA3/ -name "*.$type" | wc -l)
			printf "%s\n" "$type: $count" 
		done
	else 
		printf "%s\n" "-Error: command not found"
	fi
done